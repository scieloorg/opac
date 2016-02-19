# coding: utf-8

import unittest
import re
from flask.ext.testing import TestCase
from flask import current_app, url_for
from flask_admin.contrib.sqla import form as admin_form
from flask_login import current_user, login_user
from app import dbsql, mail
from app.utils import create_user, get_timed_serializer
from app.admin import forms
from app.controllers import get_user_by_email
from app.notifications import send_confirmation_email
from base import BaseTestCase


reset_pwd_url_pattern = re.compile('href="(.*)">')
email_confirm_url_pattern = re.compile('href="(.*)">')


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
        Quando:
            acessamos a pagina o admin/index, sem ter feito login.
        Verificamos:
            que é feito um redirect para admin/login
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
        Quando:
            acessamos a pagina o admin/index, sem ter feito login.
        Verificamos:
            que é feito um redirect para admin/login
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
        Com:
            dados válido para fazer login, de um usuário que *NÃO* existe.
        Quando:
            tentamos fazer login com esses dados.
        Verificamos:
            - a pagina visualizada corresponde ao login.
            - a pagina visualizada contem uma mensagem indicando: usuário inválido.
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
        Com:
            dados para fazer login: email inválida, senha válida.
        Quando:
            tentamos fazer login com esses dados.
        Verificamos:
            - a pagina visualizada corresponde ao login.
            - a pagina visualizada contem uma mensagem indicando:
                email inválido e usuário inválido.
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
        Com:
            dados para fazer login: email válido, senha inválida.
        Quando:
            tentamos fazer login com esses dados.
        Verificamos:
            - a pagina visualizada corresponde ao login.
            - a pagina visualizada contem uma mensagem indicando senha requerida.
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
        Com:
            um novo usuário (com email confirmado)
        Quando:
            o novo usuário faz login
        Verificamos:
            - a página visualizada corresponde ao admin/index
            - a página visualizada contem link para fazer logout.
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

    def test_login_valid_user_with_invalid_password_raise_error_msg(self):
        """
        Com:
            um novo usuário (com email confirmado)
        Quando:
            o novo usuário faz login, mas com a senha errada
        Verificamos:
            - a página visualizada corresponde ao admin/index
            - a página visualizada deve informar de senha inválida
        """

        # with
        login_url = url_for('admin.login_view')
        credentials = {
            'email': 'foo@example.com',
            'password': '123',
        }
        logged_page_header = u'<h1>OPAC Admin <small>da coleção: %s</small></h1>' % \
            current_app.config['OPAC_COLLECTION'].upper()

        logout_url = url_for('admin.logout_view')
        # when
        create_user(
            credentials['email'],
            credentials['password'],
            True)
        # create new user:
        response = self.client.post(
            login_url,
            data={
                'email': credentials['email'],
                'password': 'foo.bar',
            },
            follow_redirects=True)
        # then
        self.assertStatus(response, 200)
        self.assertTemplateUsed('admin/auth/login.html')
        self.assertNotIn(logged_page_header, response.data.decode('utf-8'))
        self.assertNotIn(logout_url, response.data.decode('utf-8'))

    def test_login_page_must_have_link_to_password_reset(self):
        """
        Quando:
            acessamos a pagina de login
        Verificamos:
            na pagina aparece os link para: recuperar a senha
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
        Com:
            a lista de idiomas suportados pela app
        Quando:
            acesso a pagina de login
        Verificamos:
            na pagina aparecem os links para trocar de idioma
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

    def test_login_with_unconfirmed_user_must_not_proceed(self):
        """
        Com:
            um novo usuário (com email NÃO confirmado)
        Quando:
            o novo usuário faz login, com os dados certos
        Verificamos:
            - a página visualizada corresponde a admin/auth/unconfirm_email.html.
            - a página visualizada deve informar do erro.
        """
        # with
        login_url = url_for('admin.login_view')
        credentials = {
            'email': 'foo@example.com',
            'password': '123',
        }
        expected_form_error = {'password': [u'Senha inválida']}
        expected_error_msgs = [
            u"Email não confirmado!",
            u"Você <strong>deve</strong> confirmar seu email.<br>",
            u"<strong>Por favor entre em contato com o administrador.</strong>"]
        create_user(
            credentials['email'],
            credentials['password'],
            False)
        # when
        # create new user:
        response = self.client.post(
            login_url,
            data=credentials,
            follow_redirects=True)
        # then
        self.assertStatus(response, 200)
        self.assertTemplateUsed('admin/auth/unconfirm_email.html')
        for msg in expected_error_msgs:
            self.assertIn(msg, response.data.decode('utf-8'))

        context_form = self.get_context_variable('form')
        self.assertIsInstance(context_form, forms.LoginForm)
        self.assertEqual(expected_form_error, context_form.errors)

    def test_logout_successfully(self):
        """
        Com:
            um novo usuário (com email confirmado).
        Quando:
            usuario faz login, e depois logout
        Verificamos:
            a operação (logout) é realizada com sucesso
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
        Com:
            um novo usuário (com email confirmado).
        Quando:
            solicitamos a recuperação de senha.
        Verificamos:
            a pagina carregada é a esperad com o formulario esperado
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
        Com:
            um novo usuário (com email confirmado).
        Quando:
            solicitamos a recuperação de senha.
        Verificamos:
            deve mostrar uma pagina 404 com o aviso
            de usuário não encontrado.
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
        Com:
            um novo usuário (com email confirmado).
        Quando:
            solicitamos a recuperação de senha.
        Verificamos:
            A notifiação (flash) na página de que foram enviadas
            as instruções para o email do novo usuário.
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

    def test_reset_password_of_valid_user_email_sent(self):
        """
        Com:
            um novo usuário (com email confirmado)
        Quando:
            solicitar a recuperação de senha
        Verificamos:
            Que a mensagem no email enviado contém o
            link para continuar a operação.
        """

        # with
        reset_pwd_url = url_for('admin.reset')
        credentials = {
            'email': 'foo@bar.com',
            'password': '123'
        }
        expected_email = {
            'subject': 'Instruções para recuperar sua senha',
            'recipients': [credentials['email'], ],
            'body_has_link': u'<a href="http://localhost%s' % reset_pwd_url
        }

        # when
        create_user(credentials['email'], credentials['password'], True)
        with mail.record_messages() as outbox:
            response = self.client.post(
                reset_pwd_url,
                data={'email': credentials['email']},
                follow_redirects=True)
            # then
            self.assertStatus(response, 200)

            self.assertEqual(1, len(outbox))
            email_msg = outbox[0]
            self.assertEqual(expected_email['subject'], email_msg.subject)
            self.assertEqual(expected_email['recipients'], email_msg.recipients)
            self.assertIn(expected_email['body_has_link'], email_msg.html.decode('utf-8'))

    def test_reset_password_send_valid_link_via_email(self):
        """
        Com:
            um novo usuário (com email confirmado),
        Quando:
            solicitamos recuperar senha, e obtemos o email com
            a url necessária para concluir a operação.
        Verificamos:
            - o email enviado contém um link para recupear senha.
            - a pagina de recuparar senha com token seja a correta.
        """

        # with
        reset_pwd_url = url_for('admin.reset')
        credentials = {
            'email': 'foo@bar.com',
            'password': '123'
        }

        # when
        create_user(credentials['email'], credentials['password'], True)
        with mail.record_messages() as outbox:
            response = self.client.post(
                reset_pwd_url,
                data={'email': credentials['email']},
                follow_redirects=True)
            # then
            self.assertEqual(1, len(outbox))
            email_msg = outbox[0]
            # recupero os links do email
            links_found = reset_pwd_url_pattern.findall(email_msg.html)
            # tem pelo menos 1 link, e tem só um link para o reset/password com token
            self.assertGreaterEqual(1, len(links_found))
            resert_url_with_token = [url for url in links_found if reset_pwd_url in url]
            self.assertEqual(1, len(resert_url_with_token))
            resert_url_with_token = resert_url_with_token[0]

        # requisição de reset passoword com token
        reset_pwd_response = self.client.get(
            resert_url_with_token,
            follow_redirects=True)
        self.assertStatus(reset_pwd_response, 200)
        self.assertTemplateUsed('admin/auth/reset_with_token.html')
        context_form = self.get_context_variable('form')
        self.assertIsInstance(context_form, forms.PasswordForm)

    def test_link_sent_via_email_to_reset_password_works_fine(self):
        """
        Com:
            um novo usuário (com email confirmado),
        Quando:
            1. solicitamos recuperar senha.
            2. obtemos o email com a url necessária para recuperação.
            3. e solicitamos uma nova senha, com o link do email.
            4. inserimos uma nova senha para o úsuario.
        Verificamos:
            - a pagina de recuperar senha tenha o form esperado.
            - a senha do usuário deve ser atualizada.
        """

        # with
        reset_pwd_url = url_for('admin.reset')
        credentials = {
            'email': 'foo@bar.com',
            'password': '123'
        }

        # when
        create_user(credentials['email'], credentials['password'], True)
        with mail.record_messages() as outbox:
            response = self.client.post(
                reset_pwd_url,
                data={'email': credentials['email']},
                follow_redirects=True)
            # then
            self.assertEqual(1, len(outbox))
            email_msg = outbox[0]
            # recupero os links do email
            links_found = reset_pwd_url_pattern.findall(email_msg.html)
            # tem pelo menos 1 link, e tem só um link para o reset/password com token
            self.assertGreaterEqual(1, len(links_found))
            resert_url_with_token = [url for url in links_found if reset_pwd_url in url][0]

        new_password = 'blaus'
        response = self.client.post(
                resert_url_with_token,
                data={'password': new_password},
                follow_redirects=True)
        self.assertStatus(response, 200)
        # verificação da nova senha do usuario
        user = get_user_by_email(credentials['email'])
        self.assertTrue(user.is_correct_password(new_password))

    def test_reset_password_with_invalid_password_raise_validation_error(self):
        """
        Com:
            um novo usuário (com email confirmado),
        Quando:
            1. solicitamos recuperar senha.
            2. obtemos o email com a url necessária para recuperação.
            3. e solicitamos uma nova senha, com o link do email.
            4. inserimos uma senha inválida ('')
        Verificamos:
            - a pagina deve informar de que senha é requerida
            - a senha do usuário não deve ser modificada
        """

        # with
        reset_pwd_url = url_for('admin.reset')
        credentials = {
            'email': 'foo@bar.com',
            'password': '123'
        }

        # when
        create_user(credentials['email'], credentials['password'], True)
        with mail.record_messages() as outbox:
            response = self.client.post(
                reset_pwd_url,
                data={'email': credentials['email']},
                follow_redirects=True)
            # then
            self.assertEqual(1, len(outbox))
            email_msg = outbox[0]
            # recupero os links do email
            links_found = reset_pwd_url_pattern.findall(email_msg.html)
            # tem pelo menos 1 link, e tem só um link para o reset/password com token
            self.assertGreaterEqual(1, len(links_found))
            resert_url_with_token = [url for url in links_found if reset_pwd_url in url][0]

        invalid_password = ''
        response = self.client.post(
                resert_url_with_token,
                data={'password': invalid_password},
                follow_redirects=True)
        self.assertStatus(response, 200)
        context_form = self.get_context_variable('form')
        expected_form_error = {'password': [u'This field is required.']}
        self.assertEqual(expected_form_error, context_form.errors)
        self.assertIn(expected_form_error['password'][0], response.data.decode('utf-8'))
        user = get_user_by_email(credentials['email'])
        self.assertFalse(user.is_correct_password(invalid_password))

    def test_reset_password_with_unconfirmed_email_shows_unconfirm_email_error(self):
        """
        Com:
            um novo usuário (com email NÃO confirmado),
        Quando:
            1. solicitamos recuperar senha.
            2. obtemos o email com a url necessária para recuperação.
            3. e solicitamos uma nova senha, com o link (token) do email.
        Verificamos:
            - a pagina deve informar que é necessário confirmar o email.
            - a troca de senha não procede.
            - a pagina deve mostrar o template admin/auth/unconfirm_email.html
        """

        # with
        reset_pwd_url = url_for('admin.reset')
        credentials = {
            'email': 'foo@bar.com',
            'password': '123'
        }

        # when
        create_user(credentials['email'], credentials['password'], False)
        with mail.record_messages() as outbox:
            response = self.client.post(
                reset_pwd_url,
                data={'email': credentials['email']},
                follow_redirects=True)
            # then
            # no foi enviado nenhum email
            self.assertEqual(0, len(outbox))
            self.assertStatus(response, 200)
            self.assertTemplateUsed('admin/auth/unconfirm_email.html')
            user = get_user_by_email(credentials['email'])
            self.assertTrue(user.is_correct_password(credentials['password']))

    def test_reset_password_with_unconfirmed_email_raise_validation_error_2(self):
        """
        Com:
            um novo usuário (com email confirmado),
        Quando:
            1. solicitamos recuperar senha.
            2. obtemos o email com a url necessária para recuperação.
            3. mudamos o usuário para ter seu email como NÃO confirmado.
            4. e solicitamos uma nova senha, com o link (token) do email.
        Verificamos:
            - a pagina deve informar que é necessário confirmar o email.
            - a troca de senha não procede.
            - a pagina deve mostrar o template admin/auth/unconfirm_email.html
        """

        # with
        reset_pwd_url = url_for('admin.reset')
        credentials = {
            'email': 'foo@bar.com',
            'password': '123'
        }

        # when
        create_user(credentials['email'], credentials['password'], True)
        with mail.record_messages() as outbox:
            response = self.client.post(
                reset_pwd_url,
                data={'email': credentials['email']},
                follow_redirects=True)
            # then
            self.assertEqual(1, len(outbox))
            email_msg = outbox[0]
            # recupero os links do email
            links_found = reset_pwd_url_pattern.findall(email_msg.html)
            # tem pelo menos 1 link, e tem só um link para o reset/password com token
            self.assertGreaterEqual(1, len(links_found))
            resert_url_with_token = [url for url in links_found if reset_pwd_url in url][0]

        # agora o usuário tem o email NÃO confirmado.
        user = get_user_by_email(credentials['email'])
        user.email_confirmed = False
        dbsql.session.add(user)
        dbsql.session.commit()
        # tentamos recuperar a senha com o link/token do email
        new_password = '321'
        response = self.client.post(
                resert_url_with_token,
                data={'password': new_password},
                follow_redirects=True)
        self.assertStatus(response, 200)
        self.assertTemplateUsed('admin/auth/unconfirm_email.html')
        user = get_user_by_email(credentials['email'])
        self.assertTrue(user.is_correct_password(credentials['password']))

    def test_reset_password_with_invalid_token_raise_404_error_page(self):
        """
        Com:
            - token inválido
        Quando:
            solicitar a recuperação de senha com token inválido
        Verificamos:
            mostra uma pagina de erro 404 com a mensagem de erro
        """

        # with
        invalid_token = 'foo.123.faketoken'
        reset_with_token_url = url_for('admin.reset_with_token', token=invalid_token)
        expected_errors_msg = u'<p>The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.</p>'
        # when
        response = self.client.get(reset_with_token_url, follow_redirects=True)
        # then
        self.assertStatus(response, 404)
        self.assertTemplateUsed('errors/404.html')
        error_message = self.get_context_variable('message')
        self.assertEqual(expected_errors_msg, error_message)

    def test_confirm_email_with_invalid_token_raise_404_message(self):
        """
        Com:
            - token inválido
        Quando:
            solicitar a confirmação de email com token inválido
        Verificamos:
            mostra uma pagina de erro 404 com a mensagem de erro
        """

        # with
        invalid_token = 'foo.123.faketoken'
        confirm_email_url = url_for('admin.confirm_email', token=invalid_token)
        expected_errors_msg = u'<p>The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.</p>'
        # when
        response = self.client.get(confirm_email_url, follow_redirects=True)
        # then
        self.assertStatus(response, 404)
        self.assertTemplateUsed('errors/404.html')
        error_message = self.get_context_variable('message')
        self.assertEqual(expected_errors_msg, error_message)

    def test_confirmation_email_send_email_with_token(self):
        """
        Com:
            - o usuário 'administrador' logado (email confirmado)
            - um novo usuário, com email NÃO confirmado
        Quando:
            1. enviamos emails de confirmação (utilizando a ação do admin/user)
            2.
        Verificamos:
            - que o email enviado contem um link para confirmar email.
            - o email é enviado para o destinatario certo.
            - após a operação, a página é a correta.
            - as notifiação para usuário deve ser mostrada na página.
        """

        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        normal_user = {
            'email': 'foo@bar.com',
            'password': '123'
        }
        create_user(normal_user['email'], normal_user['password'], False)
        login_url = url_for('admin.login_view')
        action_payload = {
            'action': 'confirm_email',
            'rowid': get_user_by_email(normal_user['email']).id,
            'url': '/admin/user/'
        }
        expected_email_sent_notifications = [
            u"Enviamos o email de confirmação para: %s" % normal_user['email'],
            u"1 usuários foram notificados com sucesso!",
        ]
        expected_email = {
            'subject': u'Confirmação de email',
            'recipients': [normal_user['email'], ],
        }
        # when
        # login do usuario admin
        login_response = self.client.post(
            login_url,
            data=admin_user,
            follow_redirects=True)
        self.assertStatus(login_response, 200)
        self.assertTemplateUsed('admin/index.html')
        # requisição da ação para enviar email de confirmação
        with mail.record_messages() as outbox:
            action_response = self.client.post(
                '/admin/user/action/',
                data=action_payload,
                follow_redirects=True)
            # then
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            for msg in expected_email_sent_notifications:
                self.assertIn(msg, action_response.data.decode('utf-8'))

            # temos um email
            self.assertEqual(1, len(outbox))
            email_msg = outbox[0]
            # email enviado ao destinatario certo, com assunto certo
            self.assertEqual(expected_email['recipients'], email_msg.recipients)
            self.assertEqual(expected_email['subject'], email_msg.subject.decode('utf-8'))
            # pegamos o link com token
            links_found = email_confirm_url_pattern.findall(email_msg.html)
            # tem pelo menos 1 link, e tem só um link para o reset/password com token
            self.assertGreaterEqual(1, len(links_found))
            email_confirmation_url_with_token = [url for url in links_found if '/admin/confirm/' in url]
            # temos a url com o token
            self.assertEqual(1, len(email_confirmation_url_with_token))
            email_confirmation_url_with_token = email_confirmation_url_with_token[0]
            self.assertIsNotNone(email_confirmation_url_with_token)
            self.assertFalse(email_confirmation_url_with_token == '')

    def test_open_confirm_url_with_token_sent_via_email_open_the_correct_page(self):
        """
        Com:
            - o usuário 'administrador' logado (email confirmado)
            - um novo usuário, com email NÃO confirmado
        Quando:
            1. enviamos emails de confirmação (utilizando a ação do admin/user)
            2. acesssamos o link enviado por email
        Verificamos:
            - que o email enviado contem um link para confirmar email.
            - após acessar o link, a página é a correta.
            - após acessar o link, a págian mostra a notificação de operação ok.
            - após acessar o link, o usuário tem seu email confirmado.
        """

        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        normal_user = {
            'email': 'foo@bar.com',
            'password': '123'
        }
        create_user(normal_user['email'], normal_user['password'], False)
        login_url = url_for('admin.login_view')
        action_payload = {
            'action': 'confirm_email',
            'rowid': get_user_by_email(normal_user['email']).id,
            'url': '/admin/user/'
        }
        expected_msg = u'Email: %s confirmado com sucesso!' % normal_user['email']
        # when
        # login do usuario admin
        login_response = self.client.post(
            login_url,
            data=admin_user,
            follow_redirects=True)
        self.assertStatus(login_response, 200)
        # requisição da ação para enviar email de confirmação
        with mail.record_messages() as outbox:
            action_response = self.client.post(
                '/admin/user/action/',
                data=action_payload,
                follow_redirects=True)
            # then
            self.assertStatus(action_response, 200)
            # temos um email
            self.assertEqual(1, len(outbox))
            email_msg = outbox[0]
            # pegamos o link com token
            links_found = email_confirm_url_pattern.findall(email_msg.html)
            # tem pelo menos 1 link, e tem só um link para o reset/password com token
            self.assertGreaterEqual(1, len(links_found))
            email_confirmation_url_with_token = [url for url in links_found if '/admin/confirm/' in url]
            # temos a url com o token
            self.assertEqual(1, len(email_confirmation_url_with_token))
            email_confirmation_url_with_token = email_confirmation_url_with_token[0]
        # acessamos o link do email
        confirmation_response = self.client.get(email_confirmation_url_with_token, follow_redirects=True)
        self.assertStatus(confirmation_response, 200)
        self.assertTemplateUsed('admin/index.html')
        # confirmação com sucesso
        self.assertIn(expected_msg, confirmation_response.data.decode('utf-8'))
        # confirmamos alteração do usuário
        user = get_user_by_email(normal_user['email'])
        self.assertTrue(user.email_confirmed)

    def test_email_confimation_token_of_invalid_user_raise_404_error_message(self):
        """
        Com:
            - email de usuário que não existe no sistema.
        Quando:
            1. enviamos emails de confirmação (utilizando diretamente notifications.py)
            2. acesssamos o link enviado por email
        Verificamos:
            - que o email enviado contem um link para confirmar email.
            - após acessar o link, a página mostra o erro 404 com a mensagem certa.
        """
        # with
        expected_error_msg = u'Usuário não encontrado'
        fake_user_email = u'foo@bar.com'
        # when
        with mail.record_messages() as outbox:
            send_confirmation_email(fake_user_email)
            # then
            # temos um email
            self.assertEqual(1, len(outbox))
            email_msg = outbox[0]
            # pegamos o link com token
            links_found = email_confirm_url_pattern.findall(email_msg.html)
            # tem pelo menos 1 link, e tem só um link para o reset/password com token
            self.assertGreaterEqual(1, len(links_found))
            email_confirmation_url_with_token = [url for url in links_found if '/admin/confirm/' in url]
            # temos a url com o token
            self.assertEqual(1, len(email_confirmation_url_with_token))
            email_confirmation_url_with_token = email_confirmation_url_with_token[0]
        # acessamos o link do email
        confirmation_response = self.client.get(email_confirmation_url_with_token, follow_redirects=True)
        self.assertStatus(confirmation_response, 404)
        self.assertTemplateUsed('errors/404.html')
        error_msg = self.get_context_variable('message')
        self.assertEqual(error_msg, error_msg)

    @unittest.skip("Login form no lugar de um UserForm, pq?")
    def test_create_user_from_admin_page_creates_a_new_user(self):
        """
        Com:
            - usuario administrador (com email confirmado)
        Quando:
            1. acessamos /admin e cadastramos um novo usuário
            2. acesssamos o link enviado por email
        Verificamos:
            - o usuário é criado.
            - o usuário administrador é notificodo do sucesso da operação.
            - o novo usuário não tem email confirmado.
            - o novo usuário é notificado por email para confirmar email.
        """

        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        new_user = {
            'email': 'foo@bar.com',
            'password': '123'
        }
        login_url = url_for('admin.login_view')
        create_user_url = '/admin/user/new/'
        expected_msgs = [
            u'Enviamos o email de confirmação para: %s' % new_user['email'],
            u'Registro criado com sucesso.',
        ]
        # when
        with mail.record_messages() as outbox:

            with self.client as client:
                # login do usuario admin
                login_response = client.post(
                    login_url,
                    data=admin_user,
                    follow_redirects=True)
                self.assertStatus(login_response, 200)
                self.assertTemplateUsed('admin/index.html')
                self.assertTrue(current_user.is_authenticated)
                # requisição da ação para enviar email de confirmação
                create_user_response = client.post(
                    create_user_url,
                    data={'email': new_user['email']},
                    follow_redirects=True)
                # then
                self.assertStatus(create_user_response, 200)
                self.assertTemplateUsed('admin/model/list.html')
                for msg in expected_msgs:
                    self.assertIn(msg, action_response.data.decode('utf-8'))
                # temos um email
            self.assertEqual(1, len(outbox))
            email_msg = outbox[0]
            # pegamos o link com token
            links_found = email_confirm_url_pattern.findall(email_msg.html)
            # tem pelo menos 1 link, e tem só um link para o reset/password com token
            self.assertGreaterEqual(1, len(links_found))
            email_confirmation_url_with_token = [url for url in links_found if '/admin/confirm/' in url]
            # temos a url com o token
            self.assertEqual(1, len(email_confirmation_url_with_token))
            email_confirmation_url_with_token = email_confirmation_url_with_token[0]
            self.assertIsNotNone(email_confirmation_url_with_token)
            self.assertFalse(email_confirmation_url_with_token == '')
        # acessamos o link do email
        user = get_user_by_email(new_user['email'])
        confirmation_response = self.client.get(email_confirmation_url_with_token, follow_redirects=True)
        self.assertStatus(confirmation_response, 200)
        self.assertTemplateUsed('admin/index.html')
        # confirmação com sucesso
        self.assertIn(expected_msg, confirmation_response.data.decode('utf-8'))
        # confirmamos alteração do usuário
        self.assertTrue(user.email_confirmed)

    @unittest.skip("Login form no lugar de um UserForm, pq?")
    def test_try_to_create_user_without_email_must_raise_error_notification(self):
        """
        Com:
            - usuario administrador (com email confirmado)
        Quando:
            1. acessamos /admin
            2. tentamos cadastrar um novo usuário, ** sem inserir email **
        Verificamos:
            - o usuário não é criado.
            - o usuário administrado é notificodo do erro da operação.
        """

        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        new_user = {
            'email': 'foo@bar.com',
            'password': '123'
        }
        login_url = url_for('admin.login_view')
        create_user_url = '/admin/user/new/'
        expected_form_error = {'email': [u'This field is required.']}
        # when
        with mail.record_messages() as outbox:

            with self.client as client:
                # login do usuario admin
                login_response = client.post(
                    login_url,
                    data=admin_user,
                    follow_redirects=True)
                self.assertStatus(login_response, 200)
                self.assertTemplateUsed('admin/index.html')
                self.assertTrue(current_user.is_authenticated)

                # "preencher" from sem o email do novo usuário
                create_user_response = client.post(
                    create_user_url,
                    data={'email': ''},
                    follow_redirects=True)
                # then
                self.assertStatus(create_user_response, 200)
                self.assertTemplateUsed('admin/model/create.html')
                # tem erro no formulario
                context_form = self.get_context_variable('form')
                # self.assertIsInstance(context_form, admin_form.UserForm)
                self.assertEqual(expected_form_error, context_form.errors)
            # não temos email
            self.assertEqual(0, len(outbox))
