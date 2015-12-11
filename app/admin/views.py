# coding: utf-8
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
            abort(404)  # melhorar mensagem de erro para o usuário

        controllers.set_user_email_confirmed(user)
        flash('Email confimed successfully: %s.' % user.email)
        return redirect(url_for('.index'))

    @admin.expose('/reset/password', methods=('GET', 'POST'))
    def reset(self):
        form = forms.EmailForm(request.form)

        if admin.helpers.validate_form_on_submit(form):
            user = controllers.get_user_by_email(email=form.data['email'])
            if not user:
                abort(404)  # melhorar mensagem de erro para o usuário
            if not user.email_confirmed:
                return self.render('admin/auth/unconfirm_email.html')

            was_sent, error_msg = user.send_reset_password_email()
            if was_sent:
                flash('Instructions to recovery password was sent to: %s.' % user.email)
            else:
                flash(error_msg, 'error')

            return redirect(url_for('.index'))

        self._template_args['form'] = form
        return self.render('admin/auth/reset.html')

    @admin.expose('/reset/password/<token>', methods=('GET', 'POST'))
    def reset_with_token(self, token):
        try:
            ts = get_timed_serializer()
            email = ts.loads(token, salt="recover-key",
                             max_age=current_app.config['CONFIRM_EMAIL_TOKEN_MAX_AGE'])
        except:
            abort(404)

        form = forms.PasswordForm(request.form)
        if admin.helpers.validate_form_on_submit(form):
            user = controllers.get_user_by_email(email=email)
            if not user.email_confirmed:
                return self.render('admin/auth/unconfirm_email.html')

            controllers.set_user_password(user, form.password.data)
            flash('New password changed successfully')
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
            # Now we'll send the email confirmation link
            was_sent, error_msg = user.send_confirmation_email()
            if was_sent:
                flash('Confirmation email sent to: %s.' % model.email)
            else:
                flash(error_msg, 'error')

    def is_accessible(self):
        return login.current_user.is_authenticated

    @action('confirm_email', 'Send Confirmation Email', 'Are you sure you want to send confirmation email to selected users?')
    def action_send_confirm_email(self, ids):
        try:
            query = models.User.query.filter(models.User.id.in_(ids))
            count = 0
            for user in query.all():
                was_sent, error_msg = user.send_confirmation_email()
                if was_sent:
                    count += 1
                    flash('Confirmation email sent to: %s.' % user.email)
                else:
                    flash(error_msg, 'error')
            flash('%s users were successfully notified.' % count)
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash('Failed to sent email to users. %s' % str(ex), 'error')


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
        'current_status', 'acronym'
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

    @action('publish', 'Publicar', 'Are you sure you want to publish the selected itens?')
    def publish(self, ids):
        try:

            controllers.set_journal_is_public_bulk(ids, True)

            # Adicionar mais contexto sobre as consequência dessa ação
            flash('Journal(s) was successfully publish.')

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash('Failed to publish Journal(s).', 'error')

    @action('unpublish', 'Despublicar', 'Are you sure you want to unpublish the selected itens?')
    def unpublish(self, ids):
        try:

            controllers.set_journal_is_public_bulk(ids, False)

            # Adicionar mais contexto sobre as consequência dessa ação
            flash('Journal(s) was successfully publish.')

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash('Failed to publish Journal(s).', 'error')


class IssueAdminView(OpacBaseAdminView):

    column_filters = [
        'label', 'volume', 'number',
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

    @action('publish', 'Publicar', 'Are you sure you want to publish the selected itens?')
    def publish(self, ids):
        try:

            controllers.set_issue_is_public_bulk(ids, True)

            # Adicionar mais contexto sobre as consequência dessa ação
            flash('Issue(s) was successfully publish.')

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash('Failed to publish Issue(s).', 'error')

    @action('unpublish', 'Despublicar', 'Are you sure you want to unpublish the selected itens?')
    def unpublish(self, ids):
        try:

            controllers.set_issue_is_public_bulk(ids, False)

            # Adicionar mais contexto sobre as consequência dessa ação
            flash('Issue(s) was successfully publish.')

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash('Failed to publish Issue(s).', 'error')


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

    @action('rebuild_html', 'Rebuild HTML', 'Are you sure you want to rebuild the HTMLs for selected articles?')
    def action_send_confirm_email(self, ids):
        try:
            articles = controllers.filter_articles_by_ids(ids)
            count = 0
            for article in articles:
                rebuild_article_xml(article)
                count += 1
            flash('%s articles were successfully rebuilt.' % count)
        except Exception, ex:
            if not self.handle_view_exception(ex):
                raise
            flash('Failed to rebuild articles. %s' % str(ex), 'error')

    @action('publish', 'Publicar', 'Are you sure you want to publish the selected itens?')
    def publish(self, ids):
        try:

            controllers.set_article_is_public_bulk(ids, True)

            # Adicionar mais contexto sobre as consequência dessa ação
            flash('Issue(s) was successfully publish.')

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash('Failed to publish Article(s).', 'error')

    @action('unpublish', 'Despublicar', 'Are you sure you want to unpublish the selected itens?')
    def unpublish(self, ids):
        try:

            controllers.set_article_is_public_bulk(ids, False)

            # Adicionar mais contexto sobre as consequência dessa ação
            flash('Article(s) was successfully publish.')

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash('Failed to publish Article.', 'error')
