# coding: utf-8
import flask_admin as admin
import flask_login as login
from flask import url_for, redirect, render_template, request
from werkzeug.security import generate_password_hash

import forms
from app.controllers import get_user
from flask.ext.admin.contrib import sqla, mongoengine


class AdminIndexView(admin.AdminIndexView):

    @admin.expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(AdminIndexView, self).index()

    @admin.expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = forms.LoginForm(request.form)
        if admin.helpers.validate_form_on_submit(form):
            user_email = form.data['email']
            user = get_user(user_email)
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))

        self._template_args['form'] = form

        return self.render('admin/login.html')

    @admin.expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


class UserAdminView(sqla.ModelView):

    page_size = 20
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    # form_excluded_columns = ('password',)

    def on_model_change(self, form, model, is_created):
        """
        Gerando a criptografia da senha.
        """
        model.password = generate_password_hash(model.password)

    def is_accessible(self):
        return login.current_user.is_authenticated


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

    column_searchable_list = ['_id', 'title']
    column_exclude_list = [
        '_id', 'timeline', 'use_licenses', 'national_code', 'subject_categories',
        'study_areas', 'social_networks', 'title_iso', 'short_title',
        'subject_descriptors', 'init_year', 'init_vol', 'init_num',
        'final_num', 'final_vol', 'final_year', 'copyrighter',
        'online_submission_url', 'cover_url', 'logo_url', 'previous_journal_id',
        'publisher_name', 'publisher_country', 'publisher_state',
        'publisher_city', 'publisher_address', 'publisher_telephone',
        'mission', 'index_at', 'sponsors', 'issue_count', 'other_titles']


class IssueAdminView(OpacBaseAdminView):

    column_searchable_list = ['iid', 'label']
    column_exclude_list = [
        '_id', 'use_licenses', 'sections', 'cover_url', 'suppl_text',
        'spe_text', 'start_month', 'end_month', 'order', 'label', 'order',
        'bibliographic_legend']


class ArticleAdminView(OpacBaseAdminView):

    column_searchable_list = ['aid', 'title', 'domain_key']
    column_exclude_list = [
        '_id', 'section', 'is_aop', 'htmls', 'domain_key']
