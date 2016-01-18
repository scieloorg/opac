# coding: utf-8
import logging
from flask_babelex import gettext as _
from flask_babelex import lazy_gettext as __
import flask_admin as admin
from flask_admin.actions import action
import flask_login as login
from flask import url_for, redirect, render_template, request, flash, abort
from flask.ext.admin.contrib import sqla, mongoengine
from werkzeug.security import generate_password_hash
from flask import current_app

import forms
from app import models
from app import controllers
from ..utils import get_timed_serializer, rebuild_article_xml


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
            # Enviamos o email de confirmação para o usuário.
            was_sent, error_msg = model.send_confirmation_email()
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
            if not self.handle_view_exception(ex):
                raise


class OpacBaseAdminView(mongoengine.ModelView):
    page_size = 20
    can_create = False
    can_edit = False
    can_delete = False
    create_modal = True
    edit_modal = True
    can_view_details = True

    def is_accessible(self):
        return login.current_user.is_authenticated


class JournalAdminView(OpacBaseAdminView):

    column_filters = [
        'current_status', 'acronym', 'is_public'
    ]
    column_searchable_list = [
        '_id', 'title', 'print_issn', 'eletronic_issn', 'acronym',
    ]
    column_exclude_list = [
        '_id', 'timeline', 'use_licenses', 'national_code', 'subject_categories',
        'study_areas', 'social_networks', 'title_iso', 'short_title',
        'subject_descriptors', 'init_year', 'init_vol', 'init_num',
        'final_num', 'final_vol', 'final_year', 'copyrighter',
        'online_submission_url', 'cover_url', 'logo_url', 'previous_journal_id',
        'publisher_name', 'publisher_country', 'publisher_state',
        'publisher_city', 'publisher_address', 'publisher_telephone',
        'mission', 'index_at', 'sponsors', 'issue_count', 'other_titles',
        'print_issn', 'eletronic_issn',
    ]
    column_formatters = dict(
        created=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
        updated=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
        scielo_issn=lambda v, c, m, p: '%s\n%s' % (m.print_issn or '', m.eletronic_issn or ''),
    )
    column_labels = dict(
        jid=_(u'Id Periódico'),
        collections=_(u'Colecções'),
        timeline=_(u'Linha do tempo'),
        national_code=_(u'Código nacional'),
        subject_categories=_(u'Categorias de assunto '),
        study_areas=_(u'Áreas de estudo'),
        social_networks=_(u'Redes sociais'),
        title=_(u'Título'),
        title_iso=_(u'Título ISO'),
        short_title=_(u'Título curto'),
        created=_(u'Criado'),
        updated=_(u'Atualizado'),
        acronym=_(u'Acrônimo'),
        scielo_issn=_(u'ISSN SciELO'),
        print_issn=_(u'ISSN impresso'),
        eletronic_issn=_(u'ISSN eletrônico'),
        subject_descriptors=_(u'Descritores de assunto'),
        init_year=_(u'Ano inicial'),
        init_vol=_(u'Volume inicial'),
        init_num=_(u'Número inicial'),
        final_year=_(u'Ano final'),
        final_vol=_(u'Volume final'),
        final_num=_(u'Número final'),
        online_submission_url=_(u'Url da submissão online'),
        cover_url=_(u'Url do capa'),
        logo_url=_(u'Url do logotipo'),
        other_titles=_(u'Outros títulos'),
        publisher_name=_(u'Nome da editora'),
        publisher_country=_(u'País da editora'),
        publisher_state=_(u'Estado da editora'),
        publisher_city=_(u'Cidade da editora'),
        publisher_address=_(u'Direção da editora'),
        publisher_telephone=_(u'Telefone da editora'),
        mission=_(u'Missão'),
        index_at=_(u'No índice'),
        sponsors=_(u'Patrocinadores'),
        previous_journal_ref=_(u'Ref periódico anterior'),
        current_status=_(u'Situação atual'),
        issue_count=_(u'Número do fascículos'),
        is_public=_(u'É Pública')
    )

    @action('publish', _(u'Publicar'), ACTION_PUBLISH_CONFIRMATION_MSG)
    def publish(self, ids):
        try:
            controllers.set_journal_is_public_bulk(ids, True)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_(u'Periódico(s) publicado(s) com sucesso!!'))
        except Exception as ex:
            flash(_(u'Ocorreu um erro tentando publicar o(s) periódico(s)!!'), 'error')
            if not self.handle_view_exception(ex):
                raise

    @action('unpublish', _(u'Despublicar'), ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish(self, ids):
        try:
            controllers.set_journal_is_public_bulk(ids, False)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_(u'Periódico(s) despublicado com sucesso!!'))
        except Exception as ex:
            flash(_(u'Ocorreu um erro tentando publicar o(s) periódico(s)!!. Erro: %(ex)s',
                    ex=str(ex)),
                  'error')
            if not self.handle_view_exception(ex):
                raise


class IssueAdminView(OpacBaseAdminView):

    column_filters = [
        'label', 'volume', 'number', 'is_public'
    ]
    column_searchable_list = [
        'iid', 'label'
    ]
    column_exclude_list = [
        '_id', 'use_licenses', 'sections', 'cover_url', 'suppl_text',
        'spe_text', 'start_month', 'end_month', 'order', 'label', 'order',
        'bibliographic_legend'
    ]
    column_formatters = dict(
        created=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
        updated=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
    )
    column_labels = dict(
        iid=_(u'Id Fascículo'),
        journal=_(u'Periódico'),
        sections=_(u'Seções'),
        cover_url=_(u'Url do capa'),
        volume=_(u'Volume'),
        number=_(u'Número'),
        created=_(u'Criado'),
        updated=_(u'Atualizado'),
        type=_(u'Tipo'),
        suppl_text=_(u'Texto do suplemento'),
        spe_text=_(u'Texto do especial'),
        start_month=_(u'Mês inicial'),
        end_month=_(u'Mês final'),
        year=_(u'Ano'),
        label=_(u'Etiqueta'),
        order=_(u'Ordem'),
        bibliographic_legend=_(u'Lenda bibliográfica'),
        is_public=_(u'É Pública')
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
            if not self.handle_view_exception(ex):
                raise

    @action('unpublish', _(u'Despublicar'), ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish(self, ids):
        try:
            controllers.set_issue_is_public_bulk(ids, False)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_(u'Fascículo(s) despublicado(s) com sucesso!!'))
        except Exception as ex:
            flash(_(u'Ocorreu um erro tentando despublicar o(s) fascículo(s)!!. Erro: %(ex)s',
                    ex=str(ex)),
                  'error')
            if not self.handle_view_exception(ex):
                raise


class ArticleAdminView(OpacBaseAdminView):

    column_searchable_list = [
        'aid', 'title', 'domain_key'
    ]
    column_exclude_list = [
        '_id', 'section', 'is_aop', 'htmls',
        'domain_key', 'xml'
    ]
    column_details_exclude_list = [
        'xml',
    ]
    column_formatters = dict(
        created=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
        updated=lambda v, c, m, p: m.created.strftime('%Y-%m-%d %H:%M:%S'),
    )
    column_labels = dict(
        aid=_(u'Id Artigo'),
        issue=_(u'Fascículo'),
        journal=_(u'Periódico'),
        title=_(u'Título'),
        section=_(u'Seção'),
        is_aop=_(u'É AOP'),
        created=_(u'Criado'),
        updated=_(u'Atualizado'),
        htmls=_(u'HTML\'s'),
        domain_key=_(u'Chave de domínio'),
        is_public=_(u'É Pública')
    )

    @action('rebuild_html', _(u'Reconstruir HTML'), ACTION_REBUILD_CONFIRMATION_MSG)
    def rebuild_html(self, ids):
        try:
            articles = controllers.filter_articles_by_ids(ids)
            count = 0
            for article in articles:
                rebuild_article_xml(article)
                count += 1
            flash(_(u'Artigo(s) reconstruido com sucesso!!'))
        except Exception, ex:
            flash(_(u'Ocorreu um erro tentando reconstruir o(s) artigo(s)!!. Erro: %(ex)s',
                    ex=str(ex)),
                  'error')
            if not self.handle_view_exception(ex):
                raise

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
            if not self.handle_view_exception(ex):
                raise

    @action('unpublish', 'Despublicar', ACTION_UNPUBLISH_CONFIRMATION_MSG)
    def unpublish(self, ids):
        try:
            controllers.set_article_is_public_bulk(ids, False)
            # Adicionar mais contexto sobre as consequência dessa ação
            flash(_(u'Artigo(s) despublicado com sucesso!!'))
        except Exception as ex:
            flash(_(u'Ocorreu um erro tentando despublicar o(s) fascículo(s)!!. Erro: %(ex)s',
                    ex=str(ex)),
                  'error')
            if not self.handle_view_exception(ex):
                raise
