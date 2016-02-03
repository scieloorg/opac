# coding: utf-8

from flask.ext.testing import TestCase
from flask import current_app, url_for
from app import dbsql, mail
from app.utils import create_user
from app.admin import forms
from base import MongoInstance, BaseTestCase


class AdminViewsTestCase(BaseTestCase):
    def setUp(self):
        dbsql.create_all()

    def create_app(self):
        return current_app

    def tearDown(self):
        dbsql.session.remove()
        dbsql.drop_all()

    def test_unauthorized_access_to_admin_index_must_redirect(self):
        """
        Acesso ao admin/index deve fazer um redirect para admin/login
        """
        # with
        admin_index_url = url_for('admin.index')
        expected_login_url = url_for('admin.login_view')
        # when
        response = self.client.get(admin_index_url, follow_redirects=False)
        # then
        self.assertStatus(response, 302)
        self.assertEqual('text/html; charset=utf-8', response.content_type)
        self.assertRedirects(response, expected_login_url)

    def test_access_to_admin_index_must_redirect_to_login_form(self):
        """
        Acesso ao admin/index deve fazer um redirect para admin/login,
        que mostra o formulario de login
        """
        # with
        admin_index_url = url_for('admin.index')
        # when
        response = self.client.get(admin_index_url, follow_redirects=True)
        # then
        self.assertStatus(response, 200)
        self.assertEqual('text/html; charset=utf-8', response.content_type)
        self.assertTemplateUsed('admin/auth/login.html')

    def test_invalid_credentials_login_must_show_validation_error(self):
        """
        Tentando fazer um login com usuários e senha inválidos,
        Deve mostrar a msg de erro.
        """

        # with
        login_url = url_for('admin.login_view')
        login_credentials = {
            'email': 'foo@example.com',
            'password': '123'
        }
        expected_errors_msg = {
            'password': u'<span class="help-block">Usuário inválido</span>',
        }
        # when
        response = self.client.post(login_url, data=login_credentials)
        # then
        self.assertStatus(response, 200)
        self.assertTemplateUsed('admin/auth/login.html')
        self.assertIn(expected_errors_msg['password'], response.data.decode('utf-8'))

    def test_invalid_user_login_must_show_validation_error(self):
        """
        Tentando fazer um login com dados inválidos (email inválido),
        Deve mostrar a msg de erro.
        """

        # with
        login_url = url_for('admin.login_view')
        login_credentials = {
            'email': 'foo',  # email inválido
            'password': '123'
        }
        expected_errors_msg = {
            'email': u'<span class="help-block">Invalid email address.</span>',
            'password': u'<span class="help-block">Usuário inválido</span>',
        }
        # when
        response = self.client.post(login_url, data=login_credentials)
        # then
        self.assertStatus(response, 200)
        self.assertTemplateUsed('admin/auth/login.html')
        self.assertIn(expected_errors_msg['email'], response.data.decode('utf-8'))
        self.assertIn(expected_errors_msg['password'], response.data.decode('utf-8'))

    def test_invalid_password_login_must_show_validation_error(self):
        """
        Tentando fazer um login com dados inválidos, (senha vazia)
        deve mostrar a msg de erro.
        """

        # with
        login_url = url_for('admin.login_view')
        login_credentials = {
            'email': 'foo@example.com',
            'password': '',  # senha inválida
        }
        expected_errors_msg = {
            'password': u'<span class="help-block">This field is required.</span>',
        }
        # when
        response = self.client.post(login_url, data=login_credentials)
        # then
        self.assertStatus(response, 200)
        self.assertTemplateUsed('admin/auth/login.html')
        self.assertIn(expected_errors_msg['password'], response.data.decode('utf-8'))

    def test_login_successfully(self):
        """
        Login com usuário válido deve poder fazer o login,
        Verificando que apareca o admin/index.html e link de logout
        """

        # with
        login_url = url_for('admin.login_view')
        credentials = {
            'email': 'foo@example.com',
            'password': '123',
        }
        expected_page_header = u'<h1>OPAC Admin <small>da coleção: %s</small></h1>' % \
            current_app.config['OPAC_COLLECTION'].upper()

        expected_logout_url = url_for('admin.logout_view')
        # when
        create_user(
            credentials['email'],
            credentials['password'],
            True)
        # create new user:
        response = self.client.post(login_url, data=credentials, follow_redirects=True)
        # then
        self.assertStatus(response, 200)
        self.assertTemplateUsed('admin/index.html')
        self.assertIn(expected_page_header, response.data.decode('utf-8'))
        self.assertIn(expected_logout_url, response.data.decode('utf-8'))

    def test_login_page_must_have_link_to_password_reset(self):
        """
        A pagina de login, tem que mostrar um link para Recuperar Senha
        """

        # with
        login_url = url_for('admin.login_view')
        expected_reset_pwd_link = url_for('admin.reset')
        # when
        response = self.client.get(login_url, follow_redirects=True)
        # then
        self.assertStatus(response, 200)
        self.assertTemplateUsed('admin/auth/login.html')
        self.assertIn(expected_reset_pwd_link, response.data.decode('utf-8'))

    def test_login_page_must_have_set_language_links(self):
        """
        A pagina de login deve disponivilizar os links para trocar de idioma
        """

        # with
        login_url = url_for('admin.login_view')
        languages = current_app.config['LANGUAGES']
        lang_urls = {}
        for lang_code, lang_name in languages.iteritems():
            lang_urls[lang_code] = {
                'url': url_for('main.set_locale', lang_code=lang_code),
                'name': lang_name,
            }

        # when
        response = self.client.get(login_url, follow_redirects=True)

        # then
        self.assertStatus(response, 200)
        self.assertTemplateUsed('admin/auth/login.html')
        for lang_code, lang_data in lang_urls.iteritems():
            lang_url = lang_data['url']
            lang_name = lang_data['name']
            self.assertIn(lang_url, response.data.decode('utf-8'))
            self.assertIn(lang_name, response.data.decode('utf-8'))

    def test_logout_successfully(self):
        """
        Login com usuário válido deve poder fazer o logout
        """

        # with
        login_url = url_for('admin.login_view')
        logout_url = url_for('admin.logout_view')
        credentials = {
            'email': 'foo@example.com',
            'password': '123',
        }
        expected_page_header = u'<h1>OPAC Admin <small>da coleção: %s</small></h1>' % \
            current_app.config['OPAC_COLLECTION'].upper()

        # when
        create_user(credentials['email'], credentials['password'], True)
        login_response = self.client.post(login_url, data=credentials, follow_redirects=True)
        self.assertStatus(login_response, 200)
        logout_response = self.client.get(logout_url, follow_redirects=True)
        # then
        self.assertStatus(logout_response, 200)
        self.assertTemplateUsed('admin/auth/login.html')

    def test_reset_password_has_form_as_expected(self):
        """
        Acessar /reset/password carraga o formulario esperado
        """

        # with
        reset_pwd_url = url_for('admin.reset')
        expected_form = forms.EmailForm()
        # when
        response = self.client.get(reset_pwd_url)
        # then
        self.assertStatus(response, 200)
        self.assertEqual('text/html; charset=utf-8', response.content_type)
        self.assertTemplateUsed('admin/auth/reset.html')

        context_form = self.get_context_variable('form')
        self.assertIsInstance(context_form, forms.EmailForm)

    def test_reset_password_of_invalid_user_raise_404(self):
        """
        A tentativa de resetar senha de um usuário que não exite,
        Deve mostrar um mensagem de erro 404: usuário não encontrado
        """

        # with
        reset_pwd_url = url_for('admin.reset')
        user_email = 'foo@example.com'
        expected_errors_msg = u'<p>Usuário não encontrado</p>'
        # when
        response = self.client.post(reset_pwd_url, data={'email': user_email})
        # then
        self.assertStatus(response, 404)
        self.assertEqual('text/html; charset=utf-8', response.content_type)
        self.assertTemplateUsed('errors/404.html')
        error_msg = self.get_context_variable('message')
        self.assertEqual(error_msg, expected_errors_msg)

    def test_reset_password_of_valid_user_proceed_ok(self):
        """
        A tentativa de resetar senha de um usuário que não exite,
        Deve mostrar um mensagem de erro 404: usuário não encontrado
        """
        credentials = {
            'email': 'foo@bar.com',
            'password': '123'
        }
        # with
        reset_pwd_url = url_for('admin.reset')
        expected_msg = u'Enviamos as instruções para recuperar a senha para: %s' % \
            credentials['email']
        # when
        create_user(credentials['email'], credentials['password'], True)
        response = self.client.post(
            reset_pwd_url,
            data={'email': credentials['email']},
            follow_redirects=True)
        # then
        self.assertStatus(response, 200)
        self.assertTemplateUsed('admin/auth/login.html')
        self.assertIn(expected_msg, response.data.decode('utf-8'))

        # TODO: validar email enviado?
        # ver: https://pythonhosted.org/Flask-Mail/#unit-tests-and-suppressing-emails
        # If the setting TESTING is set to True, emails will be suppressed.
