# coding: utf-8
import logging
from uuid import uuid4
from flask_babelex import gettext as _
from flask_babelex import lazy_gettext as __
import flask_admin as admin
from flask_admin.actions import action
from flask_admin.model.form import InlineFormAdmin
import flask_login as login
from flask import url_for, redirect, request, flash, abort
from flask.ext.admin.contrib import sqla, mongoengine
from flask.ext.admin.contrib.mongoengine.tools import parse_like_term
from flask import current_app
from mongoengine import StringField, EmailField, URLField, ReferenceField, EmbeddedDocumentField

from app import models, controllers, choices
from app.admin import forms
from app.admin.custom_filters import get_flt, CustomFilterConverter
from app.utils import get_timed_serializer, rebuild_article_xml
from opac_schema.v1.models import Sponsor


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
            except ValueError, e:
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
    column_exclude_list = ('_id', )
    inline_models = (InlineFormAdmin(Sponsor),)


class JournalAdminView(OpacBaseAdminView):

    column_filters = [
        'use_licenses', 'current_status', 'index_at', 'is_public', 'unpublish_reason'
    ]
    column_searchable_list = [
        '_id', 'title', 'title_iso', 'short_title', 'print_issn', 'eletronic_issn', 'acronym',
    ]
    column_exclude_list = [
        '_id', 'timeline', 'use_licenses', 'subject_categories',
        'study_areas', 'social_networks', 'title_iso', 'short_title',
        'subject_descriptors', 'copyrighter','online_submission_url',
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
        'iid', 'journal', 'volume', 'number', 'label', 'bibliographic_legend'
    ]
    column_exclude_list = [
        '_id', 'use_licenses', 'sections', 'cover_url', 'suppl_text',
        'spe_text', 'start_month', 'end_month', 'order', 'label', 'order',
        'bibliographic_legend', 'unpublish_reason'
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
        bibliographic_legend=__(u'Legenda bibliográfica'),
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
        '_id', 'section', 'is_aop', 'htmls',
        'domain_key', 'xml', 'unpublish_reason'
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

    @action('rebuild_html', _(u'Reconstruir HTML'), ACTION_REBUILD_CONFIRMATION_MSG)
    def rebuild_html(self, ids):
        try:
            articles = controllers.get_articles_by_aid(ids)
            count = 0
            for article in articles.itervalues():
                rebuild_article_xml(article)
                count += 1
            flash(_(u'Artigo(s) reconstruido com sucesso!!'))
        except Exception, ex:
            flash(_(u'Ocorreu um erro tentando reconstruir o(s) artigo(s)!!. Erro: %(ex)s',
                    ex=str(ex)),
                  'error')

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
