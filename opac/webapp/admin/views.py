# coding: utf-8
import os
import logging
import socket
from datetime import datetime
from functools import partial
from uuid import uuid4
from werkzeug import secure_filename
from jinja2 import Markup
from flask_babelex import gettext as _
from flask_babelex import ngettext
from flask_babelex import lazy_gettext as __
import flask_admin as admin
from flask_admin.actions import action
from flask_admin.form import Select2Field
from wtforms.fields import SelectField
from wtforms import fields as wtforms_fields
from flask_admin.model.form import InlineFormAdmin
import flask_login as login
from flask import url_for, redirect, request, flash, abort, current_app
from flask_admin.contrib import sqla, mongoengine
from flask_admin.contrib.mongoengine.tools import parse_like_term
from mongoengine import StringField, EmailField, URLField, ReferenceField, EmbeddedDocumentField
from mongoengine.base.datastructures import BaseList

from webapp import models, controllers, choices, custom_filters
from webapp.admin import forms, custom_fields
from webapp.admin.custom_filters import get_flt, CustomFilterConverter, CustomFilterConverterSqla
from webapp.admin.ajax import CustomQueryAjaxModelLoader
from webapp.utils import get_timed_serializer, import_feed
from opac_schema.v1.models import Sponsor, Journal, Issue, Article
from webapp.admin.custom_widget import CKEditorField

ACTION_PUBLISH_CONFIRMATION_MSG = _(u'Tem certeza que quer publicar os itens selecionados?')
ACTION_UNPUBLISH_CONFIRMATION_MSG = _(u'Tem certeza que quer despublicar os itens selecionados?')
ACTION_REBUILD_CONFIRMATION_MSG = _(u'Tem certeza que quer reconstruir os artigos selecionados?')
ACTION_SEND_EMAIL_CONFIRMATION_MSG = _(u'Tem certeza que quer enviar email de confirmação aos usuários selecionados?')

logger = logging.getLogger(__name__)


class AdminIndexView(admin.AdminIndexView):

    @admin.expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        counts = {
            'journals_total_count': controllers.count_elements_by_type_and_visibility('journal', public_only=False),
            'journals_public_count': controllers.count_elements_by_type_and_visibility('journal', public_only=True),
            'issues_total_count': controllers.count_elements_by_type_and_visibility('issue', public_only=False),
            'issues_public_count': controllers.count_elements_by_type_and_visibility('issue', public_only=True),
            'articles_total_count': controllers.count_elements_by_type_and_visibility('article', public_only=False),
            'articles_public_count': controllers.count_elements_by_type_and_visibility('article', public_only=True),
        }
        self._template_args['counts'] = counts
        return super(AdminIndexView, self).index()

    @admin.expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = forms.LoginForm(request.form)
        if admin.helpers.validate_form_on_submit(form):
            user_email = form.data['email']
            user = controllers.get_user_by_email(user_email)
            if not user.email_confirmed:
                return self.render('admin/auth/unconfirm_email.html')
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))

        self._template_args['form'] = form

        return self.render('admin/auth/login.html')

    @admin.expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))

    @admin.expose('/confirm/<token>', methods=('GET',))
    def confirm_email(self, token):
        try:
            ts = get_timed_serializer()
            email = ts.loads(token, salt="email-confirm-key",
                             max_age=current_app.config['TOKEN_MAX_AGE'])
        except Exception as e:  # possiveis exceções: https://pythonhosted.org/itsdangerous/#exceptions
            # qualquer exeção invalida a operação de confirmação
            abort(404)  # melhorar mensagem de erro para o usuário

        user = controllers.get_user_by_email(email=email)
        if not user:
            abort(404, _(u'Usuário não encontrado'))

        controllers.set_user_email_confirmed(user)
        flash(_(u'Email: %(email)s confirmado com sucesso!', email=user.email))
        return redirect(url_for('.index'))

    @admin.expose('/reset/password', methods=('GET', 'POST'))
    def reset(self):
        form = forms.EmailForm(request.form)

        if admin.helpers.validate_form_on_submit(form):
            user = controllers.get_user_by_email(email=form.data['email'])
            if not user:
                abort(404, _(u'Usuário não encontrado'))
            if not user.email_confirmed:
                return self.render('admin/auth/unconfirm_email.html')

            was_sent, error_msg = user.send_reset_password_email()
            if was_sent:
                flash(_(u'Enviamos as instruções para recuperar a senha para: %(email)s',
                        email=user.email))
            else:
                flash(_(u'Ocorreu um erro no envio das instruções por email para: %(email)s. Erro: %(error)s',
                        email=user.email,
                        error=error_msg),
                      'error')

            return redirect(url_for('.index'))

        self._template_args['form'] = form
        return self.render('admin/auth/reset.html')

    @admin.expose('/reset/password/<token>', methods=('GET', 'POST'))
    def reset_with_token(self, token):
        try:
            ts = get_timed_serializer()
            email = ts.loads(token, salt="recover-key",
                             max_age=current_app.config['TOKEN_MAX_AGE'])
        except Exception as e:
            abort(404)

        form = forms.PasswordForm(request.form)
        if admin.helpers.validate_form_on_submit(form):
            user = controllers.get_user_by_email(email=email)
            if not user.email_confirmed:
                return self.render('admin/auth/unconfirm_email.html')

            controllers.set_user_password(user, form.password.data)
            flash(_(u'Nova senha salva com sucesso!!'))
            return redirect(url_for('.index'))

        self._template_args['form'] = form
        self._template_args['token'] = token
        return self.render('admin/auth/reset_with_token.html')


class UserAdminView(sqla.ModelView):

    page_size = 20
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    form_excluded_columns = ('password', 'email_confirmed')
    column_filters = ['email']

    def after_model_change(self, form, model, is_created):
        if is_created:
            try:
                was_sent, error_msg = model.send_confirmation_email()
            except (ValueError, socket.error) as e:
                was_sent = False
                error_msg = e.message
            # Enviamos o email de confirmação para o usuário.
            if was_sent:
                flash(_(u'Enviamos o email de confirmação para: %(email)s',
                        email=model.email))
            else:
                flash(_(u'Ocorreu um erro no envio do email de confirmação para: %(email)s',
                        email=model.email),
                      'error')

    def is_accessible(self):
        return login.current_user.is_authenticated

    @action('confirm_email', _(u'Enviar email de confirmação'), ACTION_SEND_EMAIL_CONFIRMATION_MSG)
    def action_send_confirm_email(self, ids):
        try:
            query = models.User.query.filter(models.User.id.in_(ids))
            count = 0
            for user in query.all():
                was_sent, error_msg = user.send_confirmation_email()
                if was_sent:
                    count += 1
                    flash(_(u'Enviamos o email de confirmação para: %(email)s',
                            email=user.email))
                else:
                    flash(_(u'Ocorreu um erro no envio do email de confirmação para: %(email)s',
                            email=user.email),
                          'error')

            flash(_(u'%(count)s usuários foram notificados com sucesso!', count=count))
        except Exception as ex:
            flash(_(u'Ocorreu um erro no envio do emails de confirmação. Erro: %(ex)s',
                    ex=str(ex)),
                  'error')


class AssetsMixin(object):
    form_choices = {
        'language': models.LANGUAGES_CHOICES,
    }
    column_searchable_list = ['name', ]

    filter_converter = CustomFilterConverterSqla()

    def is_accessible(self):
        return login.current_user.is_authenticated


class FileAdminView(AssetsMixin, sqla.ModelView):

    def _path_formatter(self, context, model, name):
        return Markup("<a href='{url}' target='_blank'>Open</a>".format(
            url=model.get_absolute_url))

    column_list = ('name', 'path', 'language')
    column_formatters = {
        'path': _path_formatter,
    }
    column_filters = [
        'language'
    ]

    form_overrides = {
        'path': custom_fields.MediaFileUploadField
    }

    column_labels = dict(
        name=__(u'Nome'),
        path=__(u'Link'),
        language=__(u'Idioma'),
    )


class ImageAdminView(AssetsMixin, sqla.ModelView):

    def _path_formatter(self, context, model, name):
        return Markup(
            "<a href='{url}' target='_blank'>Open</a>".format(
                url=model.get_absolute_url))

    def _preview_formatter(self, context, model, name):
        if not model.path:
            return ''
        else:
            return Markup("<img src='{url}'>".format(
                url=model.get_thumbnail_absolute_url))

    column_list = ('name', 'preview', 'path', 'language')
    column_formatters = {
        'preview': _preview_formatter,
        'path': _path_formatter,
    }
    column_filters = [
        'language'
    ]

    form_overrides = {
        'path': custom_fields.MediaImageUploadField
    }

    column_labels = dict(
        name=__(u'Nome'),
        preview=__(u'Previsualização'),
        path=__(u'Link'),
        language=__(u'Idioma'),
    )


class OpacBaseAdminView(mongoengine.ModelView):
    page_size = 20
    can_create = False
    can_edit = False
    can_delete = False
    create_modal = True
    edit_modal = True
    can_view_details = True
    allowed_search_types = (
        StringField,
        URLField,
        EmailField,
        EmbeddedDocumentField,
        ReferenceField
    )
    filter_converter = CustomFilterConverter()
    object_id_converter = unicode

    def _search(self, query, search_term):
        op, term = parse_like_term(search_term)

        criteria = None

        for field in self._search_fields:
            flt = get_flt(field, term, op)

            if criteria is None:
                criteria = flt
            else:
                criteria |= flt
        return query.filter(criteria)

    def is_accessible(self):
        return login.current_user.is_authenticated


class NewsAdminView(OpacBaseAdminView):
    can_create = False
    can_edit = True
    can_delete = True
    page_size = 30

    list_template = 'admin/news/list.html'

    def _url_formatter(self, context, model, name):
        return Markup("<a href='{url}' target='_blank'>Open</a>".format(
            url=model.url))

    def _preview_formatter(self, context, model, name):
        if not model.image_url:
            return ''
        else:
            return Markup("<img src='{url}'>".format(
                url=model.image_url))

    def _preview_date_format(self, context, model, name):
        return custom_filters.datetimefilter(model.publication_date)

    column_formatters = {
        'url': _url_formatter,
        'image_url': _preview_formatter,
        'publication_date': _preview_date_format,
    }

    form_overrides = dict(
        language=Select2Field,
    )
    form_args = dict(
        language=dict(choices=choices.LANGUAGES_CHOICES),
    )
    column_exclude_list = (
        '_id', 'description',
    )
    column_filters = [
        'language'
    ]
    column_searchable_list = [
        '_id', 'title', 'description',
    ]

    @admin.expose('/feeds/import/from/<string:feed_name>/<string:feed_lang>')
    def feeds_import_from(self, feed_name, feed_lang):
        try:
            feeds = current_app.config['RSS_NEWS_FEEDS']

            if feed_lang not in feeds.keys():
                msg = _(u'O idioma: %s, não consta no nosso cadastro de feeds.' % (
                    feed_lang))
                flash(msg, 'error')
            elif feed_name not in feeds[feed_lang]['display_name']:
                msg = _(u'O feed: "%s", no idioma: "%s", não consta no nosso cadastro de feeds.' % (
                    feed_name, feed_lang))
                flash(msg, 'error')
            else:
                feed_url = feeds[feed_lang]['url']
                imported_ok, error_msg = import_feed(feed_url, feed_lang)
                if imported_ok:
                    msg = _(u'O feed: %s [%s], foi importado com sucesso !!' % (
                        feed_name, feed_lang))
                    flash(msg)
                else:
                    # logger.error(error_msg)
                    msg = _(u'Ocorreu um erro tentando importar o feed: %s [%s].' % (
                        feed_name, feed_lang))
                    flash(msg, 'error')
        except Exception as ex:
            msg = _(u'Ocorreu um erro tentando atualizar os feed RSS!!, %s' % str(ex))
            flash(msg, 'error')
        return redirect(url_for('.index_view'))

    @admin.expose('/feeds/import/all/')
    def feeds_import_all(self):
        try:
            feeds = current_app.config['RSS_NEWS_FEEDS']
            for language, feed in feeds.iteritems():
                imported_ok, error_msg = import_feed(feed['url'], language)
                if imported_ok:
                    flash(_(u'O feed: %s [%s], foi importado com sucesso !!' % (
                        feed['display_name'], language)))
                else:
                    # logger.error(error_msg)
                    flash(_(u'Ocorreu um erro tentando importar o feed: %s [%s].' % (
                        feed['display_name'], language)), 'error')
        except Exception as ex:
            flash(_(u'Ocorreu um erro tentando atualizar os feed RSS!!, %s' % str(ex)), 'error')
        return redirect(url_for('.index_view'))


class SponsorAdminView(OpacBaseAdminView):
    can_create = True
    can_edit = True
    can_delete = True
    create_modal = True
    edit_modal = True
    can_view_details = True
    column_exclude_list = ('_id', )
    column_searchable_list = ('name',)

    def on_model_change(self, form, model, is_created):
        # é necessario definir um valor para o campo ``_id`` na criação.
        if is_created:
            model._id = str(uuid4().hex)


class CollectionAdminView(OpacBaseAdminView):
    can_edit = True
    edit_modal = True
    form_excluded_columns = ('acronym', )
    column_exclude_list = [
        'home_logo_pt', 'home_logo_es', 'home_logo_en',
        'header_logo_pt', 'header_logo_es', 'header_logo_en',
        'menu_logo_pt', 'menu_logo_es', 'menu_logo_en',
        'logo_footer', 'logo_drop_menu'
        ]

    inline_models = (InlineFormAdmin(Sponsor),)


class JournalAdminView(OpacBaseAdminView):

    column_filters = [
        'current_status', 'index_at', 'is_public',
        'unpublish_reason'
    ]
    column_searchable_list = [
        '_id', 'title', 'title_iso', 'short_title', 'print_issn',
        'eletronic_issn', 'acronym',
    ]
    column_exclude_list = [
        '_id', 'timeline', 'subject_categories',
        'study_areas', 'social_networks', 'title_iso', 'short_title',
        'subject_descriptors', 'copyrighter', 'online_submission_url',
        'cover_url', 'logo_url', 'previous_journal_id',
        'publisher_name', 'publisher_country', 'publisher_state',
        'publisher_city', 'publisher_address', 'publisher_telephone',
        'mission', 'index_at', 'sponsors', 'issue_count', 'other_titles',
        'print_issn', 'eletronic_issn', 'unpublish_reason',
    ]
    column_formatters = dict(
        created=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
        updated=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
        scielo_issn=lambda v, c, m, p: '%s\n%s' % (m.print_issn or '', m.eletronic_issn or ''),
    )
    column_labels = dict(
        jid=__(u'Id Periódico'),
        collections=__(u'Coleções'),
        timeline=__(u'Linha do tempo'),
        subject_categories=__(u'Categorias de assunto'),
        study_areas=__(u'Áreas de estudo'),
        social_networks=__(u'Redes sociais'),
        title=__(u'Título'),
        title_iso=__(u'Título ISO'),
        short_title=__(u'Título curto'),
        created=__(u'Criado'),
        updated=__(u'Atualizado'),
        acronym=__(u'Acrônimo'),
        scielo_issn=__(u'ISSN SciELO'),
        print_issn=__(u'ISSN impresso'),
        eletronic_issn=__(u'ISSN eletrônico'),
        subject_descriptors=__(u'Descritores de assunto'),
        online_submission_url=__(u'Url da submissão online'),
        cover_url=__(u'Url do capa'),
        logo_url=__(u'Url do logotipo'),
        other_titles=__(u'Outros títulos'),
        publisher_name=__(u'Nome da editora'),
        publisher_country=__(u'País da editora'),
        publisher_state=__(u'Estado da editora'),
        publisher_city=__(u'Cidade da editora'),
        publisher_address=__(u'Endereço da editora'),
        publisher_telephone=__(u'Telefone da editora'),
        mission=__(u'Missão'),
        index_at=__(u'No índice'),
        sponsors=__(u'Patrocinadores'),
        previous_journal_ref=__(u'Ref periódico anterior'),
        current_status=__(u'Situação atual'),
        issue_count=__(u'Total de números'),
        is_public=__(u'Publicado?'),
        unpublish_reason=__(u'Motivo de despublicação'),
    )

    @action('publish', _(u'Publicar'), ACTION_PUBLISH_CONFIRMATION_MSG)
    def publish(self, ids):
        try:
            controllers.set_journal_is_public_bulk(ids, True)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_(u'Periódico(s) publicado(s) com sucesso!!'))
        except Exception as ex:
            flash(_(u'Ocorreu um erro tentando publicar o(s) periódico(s)!!'), 'error')

    def unpublish_journals(self, ids, reason):
        try:
            controllers.set_journal_is_public_bulk(ids, False, reason)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_(u'Periódico(s) despublicado com sucesso!!'))
        except Exception as ex:
            flash(_(u'Ocorreu um erro tentando despublicar o(s) periódico(s)!!. Erro: %(ex)s',
                    ex=str(ex)),
                  'error')

    @action('unpublish_by_copyright', _(u'Despublicar por %s' % choices.UNPUBLISH_REASONS[0]), ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish_by_copyright(self, ids):
        self.unpublish_journals(ids, choices.UNPUBLISH_REASONS[0])

    @action('unpublish_plagiarism', _(u'Despublicar por %s' % choices.UNPUBLISH_REASONS[1]), ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish_plagiarism(self, ids):
        self.unpublish_journals(ids, choices.UNPUBLISH_REASONS[1])

    @action('unpublish_abuse', _(u'Despublicar por %s' % choices.UNPUBLISH_REASONS[2]), ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish_abuse(self, ids):
        self.unpublish_journals(ids, choices.UNPUBLISH_REASONS[2])


class IssueAdminView(OpacBaseAdminView):

    column_filters = [
        'journal', 'volume', 'number', 'type', 'start_month',
        'end_month', 'year', 'is_public', 'unpublish_reason'
    ]
    column_searchable_list = [
        'iid', 'journal', 'volume', 'number', 'label'
    ]
    column_exclude_list = [
        '_id', 'sections', 'cover_url', 'suppl_text',
        'spe_text', 'start_month', 'end_month', 'order', 'label', 'order',
        'unpublish_reason'
    ]
    column_formatters = dict(
        created=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
        updated=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
    )
    column_labels = dict(
        iid=__(u'Id Número'),
        journal=__(u'Periódico'),
        sections=__(u'Seções'),
        cover_url=__(u'Url do capa'),
        volume=__(u'Volume'),
        number=__(u'Número'),
        created=__(u'Criado'),
        updated=__(u'Atualizado'),
        type=__(u'Tipo'),
        suppl_text=__(u'Texto do suplemento'),
        spe_text=__(u'Texto do especial'),
        start_month=__(u'Mês inicial'),
        end_month=__(u'Mês final'),
        year=__(u'Ano'),
        label=__(u'Etiqueta'),
        order=__(u'Ordem'),
        is_public=__(u'Publicado?'),
        unpublish_reason=__(u'Motivo de despublicação'),
    )

    @action('publish', _(u'Publicar'), ACTION_PUBLISH_CONFIRMATION_MSG)
    def publish(self, ids):
        try:
            controllers.set_issue_is_public_bulk(ids, True)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_(u'Fascículo(s) publicado(s) com sucesso!!'))
        except Exception as ex:
            flash(_(u'Ocorreu um erro tentando publicar o(s) fascículo(s)!!. Erro: %(ex)s',
                    ex=str(ex)),
                  'error')

    def unpublish_issues(self, ids, reason):
        try:
            controllers.set_issue_is_public_bulk(ids, False, reason)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_(u'Fascículo(s) despublicado(s) com sucesso!!'))
        except Exception as ex:
            flash(_(u'Ocorreu um erro tentando despublicar o(s) fascículo(s)!!. Erro: %(ex)s',
                    ex=str(ex)),
                  'error')

    @action('unpublish_by_copyright', _(u'Despublicar por %s' % choices.UNPUBLISH_REASONS[0]), ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish_by_copyright(self, ids):
        self.unpublish_issues(ids, choices.UNPUBLISH_REASONS[0])

    @action('unpublish_plagiarism', _(u'Despublicar por %s' % choices.UNPUBLISH_REASONS[1]), ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish_plagiarism(self, ids):
        self.unpublish_issues(ids, choices.UNPUBLISH_REASONS[1])

    @action('unpublish_abuse', _(u'Despublicar por %s' % choices.UNPUBLISH_REASONS[2]), ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish_abuse(self, ids):
        self.unpublish_issues(ids, choices.UNPUBLISH_REASONS[2])


class ArticleAdminView(OpacBaseAdminView):

    column_filters = [
        'issue', 'journal', 'is_aop', 'is_public', 'unpublish_reason'
    ]
    column_searchable_list = [
        'aid', 'issue', 'journal', 'title', 'domain_key'
    ]
    column_exclude_list = [
        '_id', 'section', 'is_aop', 'htmls', 'domain_key', 'xml',
        'unpublish_reason', 'translated_titles', 'sections', 'pdfs', 'languages',
        'original_language', 'created', 'abstract',
    ]
    column_details_exclude_list = [
        'xml',
    ]
    column_formatters = dict(
        created=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
        updated=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
    )
    column_labels = dict(
        aid=__(u'Id Artigo'),
        issue=__(u'Número'),
        journal=__(u'Periódico'),
        title=__(u'Título'),
        section=__(u'Seção'),
        is_aop=__(u'É Ahead of Print?'),
        created=__(u'Criado'),
        updated=__(u'Atualizado'),
        htmls=__(u'HTML\'s'),
        domain_key=__(u'Chave de domínio'),
        is_public=__(u'Publicado?'),
        unpublish_reason=__(u'Motivo de despublicação'),
    )

    @action('publish', _(u'Publicar'), ACTION_PUBLISH_CONFIRMATION_MSG)
    def publish(self, ids):
        try:
            controllers.set_article_is_public_bulk(ids, True)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_(u'Artigo(s) publicado com sucesso!!'))

        except Exception as ex:
            flash(_(u'Ocorreu um erro tentando publicar o(s) fascículo(s)!!. Erro: %(ex)s',
                    ex=str(ex)),
                  'error')

    def unpublish_articles(self, ids, reason):
        try:
            controllers.set_article_is_public_bulk(ids, False, reason)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_(u'Artigo(s) despublicado com sucesso!!'))
        except Exception as ex:
            flash(_(u'Ocorreu um erro tentando despublicar o(s) fascículo(s)!!. Erro: %(ex)s',
                    ex=str(ex)),
                  'error')

    @action('unpublish_by_copyright', _(u'Despublicar por %s' % choices.UNPUBLISH_REASONS[0]), ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish_by_copyright(self, ids):
        self.unpublish_articles(ids, choices.UNPUBLISH_REASONS[0])

    @action('unpublish_plagiarism', _(u'Despublicar por %s' % choices.UNPUBLISH_REASONS[1]), ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish_plagiarism(self, ids):
        self.unpublish_articles(ids, choices.UNPUBLISH_REASONS[1])

    @action('unpublish_abuse', _(u'Despublicar por %s' % choices.UNPUBLISH_REASONS[2]), ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish_abuse(self, ids):
        self.unpublish_articles(ids, choices.UNPUBLISH_REASONS[2])


class PagesAdminView(OpacBaseAdminView):
    can_create = True
    can_edit = True
    edit_modal = False
    can_delete = True
    create_modal = False
    edit_modal = False
    can_view_details = True
    column_exclude_list = ('_id', )
    column_searchable_list = ('name', 'description')

    column_exclude_list = [
        '_id', 'content',
    ]

    create_template = 'admin/pages/edit.html'
    edit_template = 'admin/pages/edit.html'

    form_overrides = dict(
        language=Select2Field,
        journal=SelectField,
        content=CKEditorField
    )

    form_args = dict(
        language=dict(choices=choices.LANGUAGES_CHOICES),
        journal=dict(choices=[('', '------')] +
                     [(journal.acronym, journal.title) for journal in controllers.get_journals()]),
    )

    def on_model_change(self, form, model, is_created):
        # é necessario definir um valor para o campo ``_id`` na criação.
        if is_created:
            model._id = str(uuid4().hex)


class PressReleaseAdminView(OpacBaseAdminView):
    can_create = True
    can_edit = True
    edit_modal = False
    can_delete = True
    create_modal = False
    edit_modal = False
    can_view_details = True
    form_excluded_columns = ('created', 'updated')
    column_searchable_list = ('title', 'content', 'doi', )

    column_exclude_list = [
        '_id', 'content', 'created', 'updated',
    ]

    create_template = 'admin/pressrelease/edit.html'
    edit_template = 'admin/pressrelease/edit.html'

    form_overrides = dict(
        language=Select2Field,
        content=CKEditorField
    )

    form_ajax_refs = {
        'journal': CustomQueryAjaxModelLoader(
            name='journal',
            model=Journal,
            fields=['title', 'acronym', 'scielo_issn', 'print_issn',
                    'eletronic_issn']
        ),
        'issue': CustomQueryAjaxModelLoader(
            name='issue',
            model=Issue,
            fields=['label', 'pid', 'journal']
        ),
        'article': CustomQueryAjaxModelLoader(
            name='article',
            model=Article,
            fields=['title', 'doi', 'pid',]
        ),
    }

    form_args = dict(
        language=dict(choices=choices.LANGUAGES_CHOICES),
    )

    def on_model_change(self, form, model, is_created):

        # é necessario definir um valor para o campo ``_id`` na criação.
        if is_created:
            model.created = datetime.now()
            model._id = str(uuid4().hex)

        model.updated = datetime.now()