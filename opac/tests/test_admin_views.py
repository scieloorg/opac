# coding: utf-8

import unittest
import re
from flask.ext.testing import TestCase
from flask import current_app, url_for
from flask_admin.contrib.sqla import form as admin_form
from flask_login import current_user, login_user
from webapp import dbsql, mail
from webapp.utils import create_user, get_timed_serializer
from webapp.admin import forms
from webapp.controllers import get_user_by_email
from webapp.notifications import send_confirmation_email
from base import BaseTestCase
from opac_schema.v1.models import Sponsor
from tests.utils import (
    makeOneJournal, makeAnyJournal,
    makeOneIssue, makeAnyIssue,
    makeOneArticle, makeAnyArticle,
    makeOneCollection, makeOneSponsor
)

reset_pwd_url_pattern = re.compile('href="(.*)">')
email_confirm_url_pattern = re.compile('href="(.*)">')


class AdminViewsTestCase(BaseTestCase):

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

    # TEST ADMIN INDEX #
    def test_admin_index_content_counts_is_ok(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina /admin
        Verificamos:
            - que a contagem de documentos (periódicos, fascículos e artigos) totais esta certa.
            - que a contagem de documentos (periódicos, fascículos e artigos) publicadas esta certa.
        """
        # with
        j_pub = makeOneJournal({'is_public': True})
        j_non_pub = makeOneJournal({'is_public': False})

        i_pub = makeOneIssue({'is_public': True, 'journal': j_pub})
        i_non_pub = makeOneIssue({'is_public': False, 'journal': j_pub})

        a_pub = makeOneArticle({'is_public': True, 'journal': j_pub, 'issue': i_pub})
        a_non_pub = makeOneArticle({'is_public': False, 'journal': j_pub, 'issue': i_pub})

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            self.assertTemplateUsed('admin/index.html')
            self.assertTrue(current_user.is_authenticated)
            # then
            counts = self.get_context_variable('counts')
            count_keys = [
                'journals_total_count',
                'journals_public_count',
                'issues_total_count',
                'issues_public_count',
                'articles_total_count',
                'articles_public_count',
            ]
            for k in count_keys:
                self.assertIn(k, count_keys)

            # contagem de periódicos
            journals_total_count = counts['journals_total_count']
            self.assertEqual(2, journals_total_count)
            journals_public_count = counts['journals_public_count']
            self.assertEqual(1, journals_public_count)
            # contagem de fascículos
            issues_total_count = counts['issues_total_count']
            self.assertEqual(2, issues_total_count)
            issues_public_count = counts['issues_public_count']
            self.assertEqual(1, issues_public_count)
            # contagem de artigos
            articles_total_count = counts['articles_total_count']
            self.assertEqual(2, articles_total_count)
            articles_public_count = counts['articles_public_count']
            self.assertEqual(1, articles_public_count)


class JournalAdminViewTests(BaseTestCase):

    def test_admin_journal_list_records(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Journal no banco
        Quando:
            - fazemos login e
            - acessamos a pagina /admin/journal/
        Verificamos:
            - o Journal criado deve estar listado nessa página
            - e o template utilizado é o esperado
        """
        # with
        journal = makeOneJournal()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            self.assertTemplateUsed('admin/index.html')
            self.assertTrue(current_user.is_authenticated)
            # acesso a aba de periódicos
            journal_list_response = client.get(url_for('journal.index_view'))
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # verificamos a resposta
            # que tem a id para acessar ao periódico
            self.assertIn(journal.id, journal_list_response.data.decode('utf-8'))
            # que tem a url para acessar ao periódico
            expected_journal_detail_url = u"/admin/journal/details/?url=%2Fadmin%2Fjournal%2F&amp;id={}".format(journal.id)
            expected_anchor = '<a class="icon" href="%s"' % expected_journal_detail_url
            self.assertIn(expected_anchor, journal_list_response.data.decode('utf-8'))

    def test_admin_journal_details(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Journal no banco
        Quando:
            - fazemos login e
            - acessamos a pagina de detalhe do periódico: /admin/journal/details/
        Verificamos:
            - a pagina mostra o periódico certo
        """
        # with
        journal = makeOneJournal()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_detail_url = url_for('journal.details_view', id=journal.id)
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            self.assertTemplateUsed('admin/index.html')
            self.assertTrue(current_user.is_authenticated)
            # acesso a aba de periódicos
            journal_detail_response = client.get(journal_detail_url)
            self.assertStatus(journal_detail_response, 200)
            self.assertTemplateUsed('admin/model/details.html')
            # then
            # verificamos a resposta
            # que tem a id para acessar ao periódico
            self.assertIn(journal.id, journal_detail_response.data.decode('utf-8'))

    def test_admin_journal_search_by_id(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Journal no banco
        Quando:
            - fazemos login e
            - acessamos a pagina de detalhe do periódico: /admin/journal/details/
            - realizamos uma busca pelo id do periódico
        Verificamos:
            - a página mostra o periódico certo
        """
        # with
        journal = makeOneJournal()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            journal_search_response = client.get(journal_index_url, data={'search': journal.id})
            self.assertStatus(journal_search_response, 200)

            # que tem a id para acessar ao periódico
            self.assertIn(journal.id, journal_list_response.data.decode('utf-8'))
            # que tem a url para acessar ao periódico
            expected_journal_detail_url = u"/admin/journal/details/?url=%2Fadmin%2Fjournal%2F&amp;id={}".format(journal.id)
            expected_anchor = '<a class="icon" href="%s"' % expected_journal_detail_url
            self.assertIn(expected_anchor, journal_list_response.data.decode('utf-8'))

    def test_admin_journal_check_column_filters(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que contém todos os column_filters esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        expected_col_filters = [
            'use_licenses',
            'current_status',
            'index_at',
            'is_public',
            'unpublish_reason'
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_filters = self.get_context_variable('admin_view').column_filters
            self.assertEqual(len(expected_col_filters), len(column_filters))
            for expected_col_filter in expected_col_filters:
                self.assertIn(expected_col_filter, column_filters)

    def test_admin_journal_check_searchable_columns(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que contém todos os campos de busca esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        expected_column_searchable_list = [
            '_id', 'title', 'title_iso', 'short_title',
            'print_issn', 'eletronic_issn', 'acronym',
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_searchable_list = self.get_context_variable('admin_view').column_searchable_list
            for expected_searchable_field in expected_column_searchable_list:
                self.assertIn(expected_searchable_field, column_searchable_list)

    def test_admin_journal_check_column_exclude_list(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que contém todos os campos excluidos da listagem são os esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        expected_column_exclude_list = [
            '_id', 'timeline', 'use_licenses', 'subject_categories',
            'study_areas', 'social_networks', 'title_iso', 'short_title',
            'subject_descriptors', 'copyrighter', 'online_submission_url',
            'cover_url', 'logo_url', 'previous_journal_id',
            'publisher_name', 'publisher_country', 'publisher_state',
            'publisher_city', 'publisher_address', 'publisher_telephone',
            'mission', 'index_at', 'sponsors', 'issue_count', 'other_titles',
            'print_issn', 'eletronic_issn', 'unpublish_reason',
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_exclude_list = self.get_context_variable('admin_view').column_exclude_list
            for expected_excluded_field in expected_column_exclude_list:
                self.assertIn(expected_excluded_field, column_exclude_list)

    def test_admin_journal_check_column_formatters(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que contém todos os formatadores de campos como são os esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        expected_column_formatters = [
            'created',
            'updated',
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_formatters = self.get_context_variable('admin_view').column_formatters
            for expected_column_formatter in expected_column_formatters:
                self.assertIn(expected_column_formatter, column_formatters.keys())

    def test_admin_journal_check_column_labels_defined(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que contém todas as etiquetas de campos esperadas
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        expected_column_labels = [
            'jid',
            'collections',
            'timeline',
            'subject_categories',
            'study_areas',
            'social_networks',
            'title',
            'title_iso',
            'short_title',
            'created',
            'updated',
            'acronym',
            'scielo_issn',
            'print_issn',
            'eletronic_issn',
            'subject_descriptors',
            'online_submission_url',
            'cover_url',
            'logo_url',
            'other_titles',
            'publisher_name',
            'publisher_country',
            'publisher_state',
            'publisher_city',
            'publisher_address',
            'publisher_telephone',
            'mission',
            'index_at',
            'sponsors',
            'previous_journal_ref',
            'current_status',
            'issue_count',
            'is_public',
            'unpublish_reason',
        ]

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_labels = self.get_context_variable('admin_view').column_labels
            for expected_column_label in expected_column_labels:
                self.assertIn(expected_column_label, column_labels.keys())

    def test_admin_journal_check_can_create_is_false(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que não permite criar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_create = self.get_context_variable('admin_view').can_create
            self.assertFalse(can_create)

    def test_admin_journal_check_can_edit_is_false(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_edit = self.get_context_variable('admin_view').can_edit
            self.assertFalse(can_edit)

    def test_admin_journal_check_can_delete_is_false(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que não permite apagar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_delete = self.get_context_variable('admin_view').can_delete
            self.assertFalse(can_delete)

    def test_admin_journal_check_create_modal_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            create_modal = self.get_context_variable('admin_view').create_modal
            self.assertTrue(create_modal)

    def test_admin_journal_check_edit_modal_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            edit_modal = self.get_context_variable('admin_view').edit_modal
            self.assertTrue(edit_modal)

    def test_admin_journal_check_can_view_details_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_view_details = self.get_context_variable('admin_view').can_view_details
            self.assertTrue(can_view_details)

    def test_admin_journal_check_actions_defined(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
        Verificamos:
            - que contém todas as etiquetas de campos esperadas
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        expected_actions = [
            'publish',
            'unpublish_abuse',
            'unpublish_by_copyright',
            'unpublish_plagiarism',
        ]

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            actions = [a[0] for a in self.get_context_variable('actions')]
            self.assertEqual(len(expected_actions), len(actions))
            for expected_action in expected_actions:
                self.assertIn(expected_action, actions)

    def test_admin_journal_action_publishing_an_unpublished_journal(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Journal no banco (is_public=False)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
            - realizamos a ação de pubilcar
        Verificamos:
            - o periódico deve ficar como público
            - o usuario é notificado do resultado da operação
        """
        # with
        journal = makeOneJournal({'is_public': False})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        expected_actions = [
            'publish',
            'unpublish_abuse',
            'unpublish_by_copyright',
            'unpublish_plagiarism',
        ]
        publish_action_url = '%saction/' % journal_index_url
        expected_msg = u'Periódico(s) publicado(s) com sucesso!!'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')

            # executamos ação publicar:
            action_response = client.post(
                publish_action_url,
                data={
                    'url': journal_index_url,
                    'action': 'publish',
                    'rowid': journal.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            journal.reload()
            self.assertTrue(journal.is_public)

    def test_admin_journal_action_publishing_a_public_journal(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Journal no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
            - realizamos a ação de pubilcar
        Verificamos:
            - o periódico deve ficar como público
            - o usuario é notificado do resultado da operação
        """
        # with
        journal = makeOneJournal({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        action_url = '%saction/' % journal_index_url
        expected_msg = u'Periódico(s) publicado(s) com sucesso!!'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': journal_index_url,
                    'action': 'publish',
                    'rowid': journal.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            journal.reload()
            self.assertTrue(journal.is_public)

    def test_admin_journal_action_unpublish_plagiarism_a_public_journal(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Journal no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
            - realizamos a ação de despublicar por plagio
        Verificamos:
            - o periódico deve ficar despublicado
            - o motivo de despublicação deve ser por: plagio
            - o usuario é notificado do resultado da operação
        """
        # with
        journal = makeOneJournal({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        action_url = '%saction/' % journal_index_url
        expected_msg = u'Periódico(s) despublicado com sucesso!!'
        expected_reason = u'Plágio'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': journal_index_url,
                    'action': 'unpublish_plagiarism',
                    'rowid': journal.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            journal.reload()
            self.assertFalse(journal.is_public)
            self.assertEqual(expected_reason, journal.unpublish_reason)

    def test_admin_journal_action_unpublish_by_copyright_a_public_journal(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Journal no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
            - realizamos a ação de despublicar por Problemas de Direitos Autorais
        Verificamos:
            - o periódico deve ficar despublicado
            - o motivo de despublicação deve ser por: Problemas de Direitos Autorais
            - o usuario é notificado do resultado da operação
        """
        # with
        journal = makeOneJournal({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        action_url = '%saction/' % journal_index_url
        expected_msg = u'Periódico(s) despublicado com sucesso!!'
        expected_reason = u'Problema de Direito Autoral'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': journal_index_url,
                    'action': 'unpublish_by_copyright',
                    'rowid': journal.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            journal.reload()
            self.assertFalse(journal.is_public)
            self.assertEqual(expected_reason, journal.unpublish_reason)

    def test_admin_journal_action_unpublish_by_abuse_a_public_journal(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Journal no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
            - realizamos a ação de despublicar por Abuso
        Verificamos:
            - o periódico deve ficar despublicado
            - o motivo de despublicação deve ser por: Abuso
            - o usuario é notificado do resultado da operação
        """
        # with
        journal = makeOneJournal({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        action_url = '%saction/' % journal_index_url
        expected_msg = u'Periódico(s) despublicado com sucesso!!'
        expected_reason = u'Abuso ou Conteúdo Indevido'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': journal_index_url,
                    'action': 'unpublish_abuse',
                    'rowid': journal.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            journal.reload()
            self.assertFalse(journal.is_public)
            self.assertEqual(expected_reason, journal.unpublish_reason)

    def test_admin_journal_action_publish_with_exception_raised_must_be_consistent(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Journal no banco (is_public=False)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
            - realizamos a ação de publicacar, mas é levantada uma exceção no processo
        Verificamos:
            - o periódico deve ficar como não público (is_public=False)
            - o usuario é notificado que houve um erro na operação
        """
        # with
        journal = makeOneJournal({'is_public': False})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        action_url = '%saction/' % journal_index_url
        expected_msg = u'Ocorreu um erro tentando publicar o(s) periódico(s)!!'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            with self.assertRaises(Exception):
                action_response = client.post(
                    action_url,
                    data={
                        'url': journal_index_url,
                        'action': 'publish',
                        'rowid': None,  # sem rowid deveria gerar uma exeção
                    },
                    follow_redirects=True
                )
                self.assertStatus(action_response, 200)
                self.assertTemplateUsed('admin/model/list.html')
                self.assertIn(expected_msg, action_response.data.decode('utf-8'))
                journal.reload()
                self.assertTrue(journal.is_public)

    def test_admin_journal_action_unpublish_for_plagiarism_with_exception_raised_must_be_consistent(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Journal no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/journal/
            - realizamos a ação de despublicacar (motivo plagio), mas é levantada uma exceção no processo
        Verificamos:
            - o periódico deve ficar como público (is_public=True)
            - o usuario é notificado que houve um erro na operação
        """
        # with
        journal = makeOneJournal({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        journal_index_url = url_for('journal.index_view')
        action_url = '%saction/' % journal_index_url
        expected_msg = u'Ocorreu um erro tentando despublicar o(s) periódico(s)!!'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            journal_list_response = client.get(journal_index_url)
            self.assertStatus(journal_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            with self.assertRaises(Exception):
                action_response = client.post(
                    action_url,
                    data={
                        'url': journal_index_url,
                        'action': 'unpublish_plagiarism',
                        'rowid': None,  # sem rowid deveria gerar uma exeção
                    },
                    follow_redirects=True
                )
                self.assertStatus(action_response, 200)
                self.assertTemplateUsed('admin/model/list.html')
                self.assertIn(expected_msg, action_response.data.decode('utf-8'))
                journal.reload()
                self.assertTrue(journal.is_public)


class IssueAdminViewTests(BaseTestCase):

    def test_admin_issue_list_records(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Issue no banco
        Quando:
            - fazemos login e
            - acessamos a pagina /admin/issue/
        Verificamos:
            - o Issue criado deve esta listado nessa página
        """
        # with
        issue = makeOneIssue()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            self.assertTemplateUsed('admin/index.html')
            self.assertTrue(current_user.is_authenticated)
            # acesso a aba de fascículos
            issue_list_response = client.get(url_for('issue.index_view'))
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # verificamos a resposta
            # que tem a id para acessar ao fascículo
            self.assertIn(issue.id, issue_list_response.data.decode('utf-8'))
            # que tem a url para acessar ao fascículo
            expected_issue_detail_url = u"/admin/issue/details/?url=%2Fadmin%2Fissue%2F&amp;id={}".format(issue.id)
            expected_anchor = '<a class="icon" href="%s"' % expected_issue_detail_url
            self.assertIn(expected_anchor, issue_list_response.data.decode('utf-8'))

    def test_admin_issue_details(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Issue no banco
        Quando:
            - fazemos login e
            - acessamos a pagina de detalhe do issue: /admin/issue/details/
        Verificamos:
            - a pagina mostra o issue certo
        """
        # with
        issue = makeOneIssue()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_detail_url = url_for('issue.details_view', id=issue.id)
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            self.assertTemplateUsed('admin/index.html')
            self.assertTrue(current_user.is_authenticated)
            # acesso a aba de periódicos
            issue_detail_response = client.get(issue_detail_url)
            self.assertStatus(issue_detail_response, 200)
            self.assertTemplateUsed('admin/model/details.html')
            # then
            # verificamos a resposta
            # que tem a id para acessar ao fascículo
            self.assertIn(issue.id, issue_detail_response.data.decode('utf-8'))

    def test_admin_issue_search_by_id(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Issue no banco
        Quando:
            - fazemos login e
            - acessamos a pagina de detalhe do issue: /admin/issue/details/
            - realizamos uma busca pelo id do issue
        Verificamos:
            - a página mostra o issue certo
        """
        # with
        issue = makeOneIssue()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de issues
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            issue_search_response = client.get(issue_index_url, data={'search': issue.id})
            self.assertStatus(issue_search_response, 200)

            # que tem a id para acessar ao periódico
            self.assertIn(issue.id, issue_list_response.data.decode('utf-8'))
            # que tem a url para acessar ao periódico
            expected_issue_detail_url = u"/admin/issue/details/?url=%2Fadmin%2Fissue%2F&amp;id={}".format(issue.id)
            expected_anchor = '<a class="icon" href="%s"' % expected_issue_detail_url
            self.assertIn(expected_anchor, issue_list_response.data.decode('utf-8'))

    def test_admin_issue_check_column_filters(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issue: /admin/issue/
        Verificamos:
            - que contém todos os column_filters esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        expected_col_filters = [
            'journal',
            'volume',
            'number',
            'type',
            'start_month',
            'end_month',
            'year',
            'is_public',
            'unpublish_reason',
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_filters = self.get_context_variable('admin_view').column_filters
            self.assertEqual(len(expected_col_filters), len(column_filters))
            for expected_col_filter in expected_col_filters:
                self.assertIn(expected_col_filter, column_filters)

    def test_admin_issue_check_searchable_columns(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issues: /admin/issue/
        Verificamos:
            - que contém todos os campos de busca esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        expected_column_searchable_list = [
            'iid', 'journal', 'volume', 'number',
            'label', 'bibliographic_legend'
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_searchable_list = self.get_context_variable('admin_view').column_searchable_list
            for expected_searchable_field in expected_column_searchable_list:
                self.assertIn(expected_searchable_field, column_searchable_list)

    def test_admin_issue_check_column_exclude_list(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issues: /admin/issue/
        Verificamos:
            - que contém todos os campos excluidos da listagem são os esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        expected_column_exclude_list = [
            '_id', 'use_licenses', 'sections', 'cover_url', 'suppl_text',
            'spe_text', 'start_month', 'end_month', 'order', 'label', 'order',
            'bibliographic_legend', 'unpublish_reason'
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_exclude_list = self.get_context_variable('admin_view').column_exclude_list
            for expected_excluded_field in expected_column_exclude_list:
                self.assertIn(expected_excluded_field, column_exclude_list)

    def test_admin_issue_check_column_formatters(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issues: /admin/issue/
        Verificamos:
            - que contém todos os formatadores de campos como são os esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        expected_column_formatters = [
            'created',
            'updated',
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_formatters = self.get_context_variable('admin_view').column_formatters
            for expected_column_formatter in expected_column_formatters:
                self.assertIn(expected_column_formatter, column_formatters.keys())

    def test_admin_issue_check_column_labels_defined(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issues: /admin/issue/
        Verificamos:
            - que contém todas as etiquetas de campos esperadas
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        expected_column_labels = [
            'iid',
            'journal',
            'sections',
            'cover_url',
            'volume',
            'number',
            'created',
            'updated',
            'type',
            'suppl_text',
            'spe_text',
            'start_month',
            'end_month',
            'year',
            'label',
            'order',
            'bibliographic_legend',
            'is_public',
            'unpublish_reason',
        ]

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_labels = self.get_context_variable('admin_view').column_labels
            for expected_column_label in expected_column_labels:
                self.assertIn(expected_column_label, column_labels.keys())

    def test_admin_issue_check_can_create_is_false(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/issue/
        Verificamos:
            - que não permite criar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_create = self.get_context_variable('admin_view').can_create
            self.assertFalse(can_create)

    def test_admin_issue_check_can_edit_is_false(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Issues: /admin/issue/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_edit = self.get_context_variable('admin_view').can_edit
            self.assertFalse(can_edit)

    def test_admin_issue_check_can_delete_is_false(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issues: /admin/issue/
        Verificamos:
            - que não permite apagar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_delete = self.get_context_variable('admin_view').can_delete
            self.assertFalse(can_delete)

    def test_admin_issue_check_create_modal_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/issue/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            create_modal = self.get_context_variable('admin_view').create_modal
            self.assertTrue(create_modal)

    def test_admin_issue_check_edit_modal_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/issue/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            edit_modal = self.get_context_variable('admin_view').edit_modal
            self.assertTrue(edit_modal)

    def test_admin_issue_check_can_view_details_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issues: /admin/issue/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_view_details = self.get_context_variable('admin_view').can_view_details
            self.assertTrue(can_view_details)

    def test_admin_issue_check_actions_defined(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issues: /admin/issue/
        Verificamos:
            - que contém todas as etiquetas de campos esperadas
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        expected_actions = [
            'publish',
            'unpublish_abuse',
            'unpublish_by_copyright',
            'unpublish_plagiarism',
        ]

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            actions = [a[0] for a in self.get_context_variable('actions')]
            self.assertEqual(len(expected_actions), len(actions))
            for expected_action in expected_actions:
                self.assertIn(expected_action, actions)

    def test_admin_issue_action_publishing_an_unpublished_issue(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Issue no banco (is_public=False)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Issue: /admin/issue/
            - realizamos a ação de pubilcar
        Verificamos:
            - o Issue deve ficar como público
            - o usuario é notificado do resultado da operação
        """
        # with
        issue = makeOneIssue({'is_public': False})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        expected_actions = [
            'publish',
            'unpublish_abuse',
            'unpublish_by_copyright',
            'unpublish_plagiarism',
        ]
        publish_action_url = '%saction/' % issue_index_url
        expected_msg = u'Fascículo(s) publicado(s) com sucesso!!'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')

            # executamos ação publicar:
            action_response = client.post(
                publish_action_url,
                data={
                    'url': issue_index_url,
                    'action': 'publish',
                    'rowid': issue.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            issue.reload()
            self.assertTrue(issue.is_public)

    def test_admin_issue_action_publishing_a_public_issue(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Issue no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issues: /admin/issue/
            - realizamos a ação de pubilcar
        Verificamos:
            - o issue deve ficar como público
            - o usuario é notificado do resultado da operação
        """
        # with
        issue = makeOneIssue({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        action_url = '%saction/' % issue_index_url
        expected_msg = u'Fascículo(s) publicado(s) com sucesso!!'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': issue_index_url,
                    'action': 'publish',
                    'rowid': issue.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            issue.reload()
            self.assertTrue(issue.is_public)

    def test_admin_issue_action_unpublish_plagiarism_a_public_issue(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Issue no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issues: /admin/issue/
            - realizamos a ação de despublicar por plagio
        Verificamos:
            - o issue deve ficar despublicado
            - o motivo de despublicação deve ser por: plagio
            - o usuario é notificado do resultado da operação
        """
        # with
        issue = makeOneIssue({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        action_url = '%saction/' % issue_index_url
        expected_msg = u'Fascículo(s) despublicado(s) com sucesso!!'
        expected_reason = u'Plágio'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': issue_index_url,
                    'action': 'unpublish_plagiarism',
                    'rowid': issue.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            issue.reload()
            self.assertFalse(issue.is_public)
            self.assertEqual(expected_reason, issue.unpublish_reason)

    def test_admin_issue_action_unpublish_by_copyright_a_public_issue(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Issue no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issues: /admin/issue/
            - realizamos a ação de despublicar por Problemas de Direitos Autorais
        Verificamos:
            - o issue deve ficar despublicado
            - o motivo de despublicação deve ser por: Problemas de Direitos Autorais
            - o usuario é notificado do resultado da operação
        """
        # with
        issue = makeOneIssue({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        action_url = '%saction/' % issue_index_url
        expected_msg = u'Fascículo(s) despublicado(s) com sucesso!!'
        expected_reason = u'Problema de Direito Autoral'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': issue_index_url,
                    'action': 'unpublish_by_copyright',
                    'rowid': issue.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            issue.reload()
            self.assertFalse(issue.is_public)
            self.assertEqual(expected_reason, issue.unpublish_reason)

    def test_admin_issue_action_unpublish_by_abuse_a_public_issue(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Issue no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de issues: /admin/issue/
            - realizamos a ação de despublicar por Abuso
        Verificamos:
            - o issue deve ficar despublicado
            - o motivo de despublicação deve ser por: Abuso
            - o usuario é notificado do resultado da operação
        """
        # with
        issue = makeOneIssue({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        action_url = '%saction/' % issue_index_url
        expected_msg = u'Fascículo(s) despublicado(s) com sucesso!!'
        expected_reason = u'Abuso ou Conteúdo Indevido'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': issue_index_url,
                    'action': 'unpublish_abuse',
                    'rowid': issue.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            issue.reload()
            self.assertFalse(issue.is_public)
            self.assertEqual(expected_reason, issue.unpublish_reason)

    def test_admin_issue_action_publish_with_exception_raised_must_be_consistent(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Issue no banco (is_public=False)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Issues: /admin/issue/
            - realizamos a ação de publicacar, mas é levantada uma exceção no processo
        Verificamos:
            - o Issue deve ficar como não público (is_public=False)
            - o usuario é notificado que houve um erro na operação
        """
        # with
        issue = makeOneIssue({'is_public': False})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        action_url = '%saction/' % issue_index_url
        expected_msg = u'Ocorreu um erro tentando despublicar o(s) fascículo(s)!!.'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            with self.assertRaises(Exception):
                action_response = client.post(
                    action_url,
                    data={
                        'url': issue_index_url,
                        'action': 'publish',
                        'rowid': None,  # sem rowid deveria gerar uma exeção
                    },
                    follow_redirects=True
                )
                self.assertStatus(action_response, 200)
                self.assertTemplateUsed('admin/model/list.html')
                self.assertIn(expected_msg, action_response.data.decode('utf-8'))
                issue.reload()
                self.assertTrue(issue.is_public)

    def test_admin_issue_action_unpublish_for_plagiarism_with_exception_raised_must_be_consistent(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Issue no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Issues: /admin/issue/
            - realizamos a ação de despublicacar (motivo plagio), mas é levantada uma exceção no processo
        Verificamos:
            - o issue deve ficar como público (is_public=True)
            - o usuario é notificado que houve um erro na operação
        """
        # with
        issue = makeOneIssue({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        issue_index_url = url_for('issue.index_view')
        action_url = '%saction/' % issue_index_url
        expected_msg = u'Ocorreu um erro tentando despublicar o(s) fascículo(s)!!.'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de Issues
            issue_list_response = client.get(issue_index_url)
            self.assertStatus(issue_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            with self.assertRaises(Exception):
                action_response = client.post(
                    action_url,
                    data={
                        'url': issue_index_url,
                        'action': 'unpublish_plagiarism',
                        'rowid': None,  # sem rowid deveria gerar uma exeção
                    },
                    follow_redirects=True
                )
                self.assertStatus(action_response, 200)
                self.assertTemplateUsed('admin/model/list.html')
                self.assertIn(expected_msg, action_response.data.decode('utf-8'))
                issue.reload()
                self.assertTrue(issue.is_public)


class ArticleAdminViewTests(BaseTestCase):

    def test_admin_article_list_records(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Article no banco
        Quando:
            - fazemos login e
            - acessamos a pagina /admin/article/
        Verificamos:
            - o Article criado deve esta listado nessa página
        """
        # with
        article = makeOneArticle({'title': u'foo bar baz'})

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            self.assertTemplateUsed('admin/index.html')
            self.assertTrue(current_user.is_authenticated)
            # acesso a aba de fascículos
            article_list_response = client.get(url_for('article.index_view'))
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # verificamos a resposta
            # que tem a id para acessar ao fascículo
            self.assertIn(article.id, article_list_response.data.decode('utf-8'))
            # que tem a url para acessar ao fascículo
            expected_article_detail_url = u"/admin/article/details/?url=%2Fadmin%2Farticle%2F&amp;id={}".format(article.id)
            expected_anchor = '<a class="icon" href="%s"' % expected_article_detail_url
            self.assertIn(expected_anchor, article_list_response.data.decode('utf-8'))

    def test_admin_article_details(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Article no banco
        Quando:
            - fazemos login e
            - acessamos a pagina de detalhe do article: /admin/article/details/
        Verificamos:
            - a pagina mostra o article certo
        """
        # with
        article = makeOneArticle()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_detail_url = url_for('article.details_view', id=article.id)
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            self.assertTemplateUsed('admin/index.html')
            self.assertTrue(current_user.is_authenticated)
            # acesso a aba de periódicos
            article_detail_response = client.get(article_detail_url)
            self.assertStatus(article_detail_response, 200)
            self.assertTemplateUsed('admin/model/details.html')
            # then
            # verificamos a resposta
            # que tem a id para acessar ao fascículo
            self.assertIn(article.id, article_detail_response.data.decode('utf-8'))

    def test_admin_article_search_by_id(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Article no banco
        Quando:
            - fazemos login e
            - acessamos a pagina de detalhe do article: /admin/article/details/
            - realizamos uma busca pelo id do article
        Verificamos:
            - a página mostra o article certo
        """
        # with
        article = makeOneArticle()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de articles
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            article_search_response = client.get(article_index_url, data={'search': article.id})
            self.assertStatus(article_search_response, 200)

            # que tem a id para acessar ao periódico
            self.assertIn(article.id, article_list_response.data.decode('utf-8'))
            # que tem a url para acessar ao periódico
            expected_article_detail_url = u"/admin/article/details/?url=%2Fadmin%2Farticle%2F&amp;id={}".format(article.id)
            expected_anchor = '<a class="icon" href="%s"' % expected_article_detail_url
            self.assertIn(expected_anchor, article_list_response.data.decode('utf-8'))

    def test_admin_article_check_column_filters(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Article: /admin/article/
        Verificamos:
            - que contém todos os column_filters esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        expected_col_filters = [
            'issue', 'journal', 'is_aop', 'is_public', 'unpublish_reason'
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_filters = self.get_context_variable('admin_view').column_filters
            self.assertEqual(len(expected_col_filters), len(column_filters))
            for expected_col_filter in expected_col_filters:
                self.assertIn(expected_col_filter, column_filters)

    def test_admin_article_check_searchable_columns(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de articles: /admin/article/
        Verificamos:
            - que contém todos os campos de busca esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        expected_column_searchable_list = [
            'aid', 'issue', 'journal', 'title', 'domain_key'
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_searchable_list = self.get_context_variable('admin_view').column_searchable_list
            self.assertEqual(len(expected_column_searchable_list), len(column_searchable_list))
            for expected_searchable_field in expected_column_searchable_list:
                self.assertIn(expected_searchable_field, column_searchable_list)

    def test_admin_article_check_column_exclude_list(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de articles: /admin/article/
        Verificamos:
            - que contém todos os campos excluidos da listagem são os esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        expected_column_exclude_list = [
            '_id', 'section', 'is_aop', 'htmls', 'domain_key', 'xml',
            'unpublish_reason', 'translated_titles', 'sections', 'pdfs', 'languages',
            'original_language', 'created'
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_exclude_list = self.get_context_variable('admin_view').column_exclude_list
            self.assertEqual(len(expected_column_exclude_list), len(column_exclude_list))
            for expected_excluded_field in expected_column_exclude_list:
                self.assertIn(expected_excluded_field, column_exclude_list)

    def test_admin_article_check_column_formatters(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de articles: /admin/article/
        Verificamos:
            - que contém todos os formatadores de campos como são os esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        expected_column_formatters = [
            'created',
            'updated',
        ]
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_formatters = self.get_context_variable('admin_view').column_formatters
            self.assertEqual(len(expected_column_formatters), len(column_formatters))
            for expected_column_formatter in expected_column_formatters:
                self.assertIn(expected_column_formatter, column_formatters.keys())

    def test_admin_article_check_column_labels_defined(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Article: /admin/article/
        Verificamos:
            - que contém todas as etiquetas de campos esperadas
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        expected_column_labels = [
            'aid',
            'issue',
            'journal',
            'title',
            'section',
            'is_aop',
            'created',
            'updated',
            'htmls',
            'domain_key',
            'is_public',
            'unpublish_reason',
        ]

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_labels = self.get_context_variable('admin_view').column_labels
            self.assertEqual(len(expected_column_labels), len(column_labels))
            for expected_column_label in expected_column_labels:
                self.assertIn(expected_column_label, column_labels.keys())

    def test_admin_article_check_can_create_is_false(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Article: /admin/article/
        Verificamos:
            - que não permite criar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_create = self.get_context_variable('admin_view').can_create
            self.assertFalse(can_create)

    def test_admin_article_check_can_edit_is_false(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Article: /admin/article/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_edit = self.get_context_variable('admin_view').can_edit
            self.assertFalse(can_edit)

    def test_admin_article_check_can_delete_is_false(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de articles: /admin/article/
        Verificamos:
            - que não permite apagar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_delete = self.get_context_variable('admin_view').can_delete
            self.assertFalse(can_delete)

    def test_admin_article_check_create_modal_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/article/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            create_modal = self.get_context_variable('admin_view').create_modal
            self.assertTrue(create_modal)

    def test_admin_article_check_edit_modal_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/article/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            edit_modal = self.get_context_variable('admin_view').edit_modal
            self.assertTrue(edit_modal)

    def test_admin_article_check_can_view_details_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de articles: /admin/article/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_view_details = self.get_context_variable('admin_view').can_view_details
            self.assertTrue(can_view_details)

    def test_admin_article_check_actions_defined(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de articles: /admin/article/
        Verificamos:
            - que contém todas as etiquetas de campos esperadas
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        expected_actions = [
            'publish',
            'unpublish_abuse',
            'unpublish_by_copyright',
            'unpublish_plagiarism',
        ]

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            actions = [a[0] for a in self.get_context_variable('actions')]
            self.assertEqual(len(expected_actions), len(actions))
            for expected_action in expected_actions:
                self.assertIn(expected_action, actions)

    def test_admin_article_action_publishing_an_unpublished_article(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Article no banco (is_public=False)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Articles: /admin/article/
            - realizamos a ação de pubilcar
        Verificamos:
            - o artigo deve ficar como público
            - o usuario é notificado do resultado da operação
        """
        # with
        article = makeOneArticle({'is_public': False})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        publish_action_url = '%saction/' % article_index_url
        expected_msg = u'Artigo(s) publicado com sucesso!!'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de artigos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')

            # executamos ação publicar:
            action_response = client.post(
                publish_action_url,
                data={
                    'url': article_index_url,
                    'action': 'publish',
                    'rowid': article.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            article.reload()
            self.assertTrue(article.is_public)

    def test_admin_article_action_publishing_a_public_article(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Article no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de articles: /admin/article/
            - realizamos a ação de pubilcar
        Verificamos:
            - o article deve ficar como público
            - o usuario é notificado do resultado da operação
        """
        # with
        article = makeOneArticle({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        action_url = '%saction/' % article_index_url
        expected_msg = u'Artigo(s) publicado com sucesso!!'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de artigos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': article_index_url,
                    'action': 'publish',
                    'rowid': article.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            article.reload()
            self.assertTrue(article.is_public)

    def test_admin_article_action_unpublish_plagiarism_a_public_article(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Article no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de articles: /admin/article/
            - realizamos a ação de despublicar por plagio
        Verificamos:
            - o article deve ficar despublicado
            - o motivo de despublicação deve ser por: plagio
            - o usuario é notificado do resultado da operação
        """
        # with
        article = makeOneArticle({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        action_url = '%saction/' % article_index_url
        expected_msg = u'Artigo(s) despublicado com sucesso!!'
        expected_reason = u'Plágio'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': article_index_url,
                    'action': 'unpublish_plagiarism',
                    'rowid': article.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            article.reload()
            self.assertFalse(article.is_public)
            self.assertEqual(expected_reason, article.unpublish_reason)

    def test_admin_article_action_unpublish_by_copyright_a_public_article(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Article no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de articles: /admin/article/
            - realizamos a ação de despublicar por Problemas de Direitos Autorais
        Verificamos:
            - o article deve ficar despublicado
            - o motivo de despublicação deve ser por: Problemas de Direitos Autorais
            - o usuario é notificado do resultado da operação
        """
        # with
        article = makeOneArticle({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        action_url = '%saction/' % article_index_url
        expected_msg = u'Artigo(s) despublicado com sucesso!!'
        expected_reason = u'Problema de Direito Autoral'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': article_index_url,
                    'action': 'unpublish_by_copyright',
                    'rowid': article.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            article.reload()
            self.assertFalse(article.is_public)
            self.assertEqual(expected_reason, article.unpublish_reason)

    def test_admin_article_action_unpublish_by_abuse_a_public_article(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Article no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de articles: /admin/article/
            - realizamos a ação de despublicar por Abuso
        Verificamos:
            - o article deve ficar despublicado
            - o motivo de despublicação deve ser por: Abuso
            - o usuario é notificado do resultado da operação
        """
        # with
        article = makeOneArticle({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        action_url = '%saction/' % article_index_url
        expected_msg = u'Artigo(s) despublicado com sucesso!!'
        expected_reason = u'Abuso ou Conteúdo Indevido'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            action_response = client.post(
                action_url,
                data={
                    'url': article_index_url,
                    'action': 'unpublish_abuse',
                    'rowid': article.id,
                },
                follow_redirects=True
            )
            self.assertStatus(action_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            self.assertIn(expected_msg, action_response.data.decode('utf-8'))
            article.reload()
            self.assertFalse(article.is_public)
            self.assertEqual(expected_reason, article.unpublish_reason)

    def test_admin_article_action_publish_with_exception_raised_must_be_consistent(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Article no banco (is_public=False)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Articles: /admin/article/
            - realizamos a ação de publicacar, mas é levantada uma exceção no processo
        Verificamos:
            - o Article deve ficar como não público (is_public=False)
            - o usuario é notificado que houve um erro na operação
        """
        # with
        article = makeOneArticle({'is_public': False})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        action_url = '%saction/' % article_index_url
        expected_msg = u'Ocorreu um erro tentando despublicar o(s) fascículo(s)!!.'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de periódicos
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            with self.assertRaises(Exception):
                action_response = client.post(
                    action_url,
                    data={
                        'url': article_index_url,
                        'action': 'publish',
                        'rowid': None,  # sem rowid deveria gerar uma exeção
                    },
                    follow_redirects=True
                )
                self.assertStatus(action_response, 200)
                self.assertTemplateUsed('admin/model/list.html')
                self.assertIn(expected_msg, action_response.data.decode('utf-8'))
                article.reload()
                self.assertTrue(article.is_public)

    def test_admin_article_action_unpublish_for_plagiarism_with_exception_raised_must_be_consistent(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Article no banco (is_public=True)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Articles: /admin/article/
            - realizamos a ação de despublicacar (motivo plagio), mas é levantada uma exceção no processo
        Verificamos:
            - o article deve ficar como público (is_public=True)
            - o usuario é notificado que houve um erro na operação
        """
        # with
        article = makeOneArticle({'is_public': True})
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        article_index_url = url_for('article.index_view')
        action_url = '%saction/' % article_index_url
        expected_msg = u'Ocorreu um erro tentando despublicar o(s) fascículo(s)!!.'
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acessamos a listagem de Issues
            article_list_response = client.get(article_index_url)
            self.assertStatus(article_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # executamos ação publicar:
            with self.assertRaises(Exception):
                action_response = client.post(
                    action_url,
                    data={
                        'url': article_index_url,
                        'action': 'unpublish_plagiarism',
                        'rowid': None,  # sem rowid deveria gerar uma exeção
                    },
                    follow_redirects=True
                )
                self.assertStatus(action_response, 200)
                self.assertTemplateUsed('admin/model/list.html')
                self.assertIn(expected_msg, action_response.data.decode('utf-8'))
                article.reload()
                self.assertTrue(article.is_public)


class CollectionAdminViewTests(BaseTestCase):

    def test_admin_collection_list_records(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Collection no banco
        Quando:
            - fazemos login e
            - acessamos a pagina /admin/collection/
        Verificamos:
            - o Collection criado deve estar listado nessa página
            - e o template utilizado é o esperado
        """
        # with
        collection = makeOneCollection()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            self.assertTemplateUsed('admin/index.html')
            self.assertTrue(current_user.is_authenticated)
            # acesso a aba de collection
            collection_list_response = client.get(url_for('collection.index_view'))
            self.assertStatus(collection_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # verificamos a resposta
            # que tem a id para acessar ao collection
            self.assertIn(collection.id, collection_list_response.data.decode('utf-8'))
            # que tem a url para acessar ao collection
            expected_collection_detail_url = u"/admin/collection/details/?url=%2Fadmin%2Fcollection%2F&amp;id={}".format(collection.id)
            expected_anchor = '<a class="icon" href="%s"' % expected_collection_detail_url
            self.assertIn(expected_anchor, collection_list_response.data.decode('utf-8'))

    def test_admin_collection_details(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Collection no banco
        Quando:
            - fazemos login e
            - acessamos a pagina de detalhe do Collection: /admin/collection/details/
        Verificamos:
            - a pagina mostra o Collection certo
        """
        # with
        collection = makeOneCollection()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        collection_detail_url = url_for('collection.details_view', id=collection.id)
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            self.assertTemplateUsed('admin/index.html')
            self.assertTrue(current_user.is_authenticated)
            # acesso a aba de Collection
            collection_detail_response = client.get(collection_detail_url)
            self.assertStatus(collection_detail_response, 200)
            self.assertTemplateUsed('admin/model/details.html')
            # then
            # verificamos a resposta
            # que tem a id para acessar ao Collection
            self.assertIn(collection.id, collection_detail_response.data.decode('utf-8'))

    def test_admin_collection_check_column_exclude_list(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de collections: /admin/collection/
        Verificamos:
            - que contém todos os campos excluidos da listagem são os esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        collection_index_url = url_for('collection.index_view')
        expected_column_exclude_list = [
            'logo_resource', 'header_alter_logo_resource',
            'header_logo_resource', 'footer_resource', '_id'
            ]

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de collections
            collection_list_response = client.get(collection_index_url)
            self.assertStatus(collection_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_exclude_list = self.get_context_variable('admin_view').column_exclude_list
            self.assertEqual(len(expected_column_exclude_list), len(column_exclude_list))
            for expected_excluded_field in expected_column_exclude_list:
                self.assertIn(expected_excluded_field, column_exclude_list)

    def test_admin_collection_check_form_excluded_columns(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de collections: /admin/collection/
        Verificamos:
            - que contém todos os campos excluidos do formulario são os esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        collection_index_url = url_for('collection.index_view')
        expected_form_excluded_columns = ('acronym', )
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de collections
            collection_list_response = client.get(collection_index_url)
            self.assertStatus(collection_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            form_excluded_columns = self.get_context_variable('admin_view').form_excluded_columns
            self.assertEqual(len(expected_form_excluded_columns), len(form_excluded_columns))
            for expected_form_excluded_column in expected_form_excluded_columns:
                self.assertIn(expected_form_excluded_column, form_excluded_columns)

    def test_admin_collection_check_can_create_is_false(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Article: /admin/collection/
        Verificamos:
            - que não permite criar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        collection_index_url = url_for('collection.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            collection_list_response = client.get(collection_index_url)
            self.assertStatus(collection_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_create = self.get_context_variable('admin_view').can_create
            self.assertFalse(can_create)

    def test_admin_collection_check_can_edit_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Article: /admin/collection/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        collection_index_url = url_for('collection.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            collection_list_response = client.get(collection_index_url)
            self.assertStatus(collection_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_edit = self.get_context_variable('admin_view').can_edit
            self.assertTrue(can_edit)

    def test_admin_collection_check_can_delete_is_false(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de collections: /admin/collection/
        Verificamos:
            - que não permite apagar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        collection_index_url = url_for('collection.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            collection_list_response = client.get(collection_index_url)
            self.assertStatus(collection_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_delete = self.get_context_variable('admin_view').can_delete
            self.assertFalse(can_delete)

    def test_admin_collection_check_create_modal_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/collection/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        collection_index_url = url_for('collection.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            collection_list_response = client.get(collection_index_url)
            self.assertStatus(collection_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            create_modal = self.get_context_variable('admin_view').create_modal
            self.assertTrue(create_modal)

    def test_admin_collection_check_edit_modal_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de periódicos: /admin/collection/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        collection_index_url = url_for('collection.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            collection_list_response = client.get(collection_index_url)
            self.assertStatus(collection_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            edit_modal = self.get_context_variable('admin_view').edit_modal
            self.assertTrue(edit_modal)

    def test_admin_collection_check_can_view_details_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de collections: /admin/collection/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        collection_index_url = url_for('collection.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            collection_list_response = client.get(collection_index_url)
            self.assertStatus(collection_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_view_details = self.get_context_variable('admin_view').can_view_details
            self.assertTrue(can_view_details)


class SponsorAdminViewTests(BaseTestCase):

    def test_admin_sponsor_list_records(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Collection no banco
        Quando:
            - fazemos login e
            - acessamos a pagina /admin/sponsor/
        Verificamos:
            - o Collection criado deve estar listado nessa página
            - e o template utilizado é o esperado
        """
        # with
        sponsor = makeOneSponsor()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            self.assertTemplateUsed('admin/index.html')
            self.assertTrue(current_user.is_authenticated)
            # acesso a aba de Sponsor
            sponsor_list_response = client.get(url_for('sponsor.index_view'))
            self.assertStatus(sponsor_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # then
            # verificamos a resposta
            # que tem a id para acessar ao sponsor
            self.assertIn(sponsor.id, sponsor_list_response.data.decode('utf-8'))
            # que tem a url para acessar ao sponsor
            expected_sponsor_detail_url = u"/admin/sponsor/details/?url=%2Fadmin%2Fsponsor%2F&amp;id={}".format(sponsor.id)
            expected_anchor = '<a class="icon" href="%s"' % expected_sponsor_detail_url
            self.assertIn(expected_anchor, sponsor_list_response.data.decode('utf-8'))

    def test_admin_sponsor_details(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
            - um novo registro do tipo: Sponsor no banco
        Quando:
            - fazemos login e
            - acessamos a pagina de detalhe do Sponsor: /admin/sponsor/details/
        Verificamos:
            - a pagina mostra o Sponsor certo
        """
        # with
        sponsor = makeOneSponsor()

        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        sponsor_detail_url = url_for('sponsor.details_view', id=sponsor.id)
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            self.assertTemplateUsed('admin/index.html')
            self.assertTrue(current_user.is_authenticated)
            # acesso a aba de Sponsor
            sponsor_detail_response = client.get(sponsor_detail_url)
            self.assertStatus(sponsor_detail_response, 200)
            self.assertTemplateUsed('admin/model/details.html')
            # then
            # verificamos a resposta
            # que tem a id para acessar ao Sponsor
            self.assertIn(sponsor.id, sponsor_detail_response.data.decode('utf-8'))

    def test_admin_sponsor_check_column_exclude_list(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de sponsors: /admin/sponsor/
        Verificamos:
            - que contém todos os campos excluidos da listagem são os esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        sponsor_index_url = url_for('sponsor.index_view')
        expected_column_exclude_list = ('_id', )
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de Sponsor
            sponsor_list_response = client.get(sponsor_index_url)
            self.assertStatus(sponsor_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_exclude_list = self.get_context_variable('admin_view').column_exclude_list
            self.assertEqual(len(expected_column_exclude_list), len(column_exclude_list))
            for expected_excluded_field in expected_column_exclude_list:
                self.assertIn(expected_excluded_field, column_exclude_list)

    def test_admin_sponsor_check_form_excluded_columns(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de sponsors: /admin/sponsor/
        Verificamos:
            - que contém todos os campos excluidos do formulario são os esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        sponsor_index_url = url_for('sponsor.index_view')
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de Sponsor
            sponsor_list_response = client.get(sponsor_index_url)
            self.assertStatus(sponsor_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            form_excluded_columns = self.get_context_variable('admin_view').form_excluded_columns
            self.assertEqual(None, form_excluded_columns)

    def test_admin_sponsor_check_can_create_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Sponsor: /admin/sponsor/
        Verificamos:
            - que não permite criar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        sponsor_index_url = url_for('sponsor.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de Sponsor
            sponsor_list_response = client.get(sponsor_index_url)
            self.assertStatus(sponsor_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_create = self.get_context_variable('admin_view').can_create
            self.assertTrue(can_create)

    def test_admin_sponsor_check_can_edit_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de Article: /admin/sponsor/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        sponsor_index_url = url_for('sponsor.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de Sponsor
            sponsor_list_response = client.get(sponsor_index_url)
            self.assertStatus(sponsor_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_edit = self.get_context_variable('admin_view').can_edit
            self.assertTrue(can_edit)

    def test_admin_sponsor_check_can_delete_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de sponsors: /admin/sponsor/
        Verificamos:
            - que não permite apagar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        sponsor_index_url = url_for('sponsor.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de sponsor
            sponsor_list_response = client.get(sponsor_index_url)
            self.assertStatus(sponsor_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_delete = self.get_context_variable('admin_view').can_delete
            self.assertTrue(can_delete)

    def test_admin_sponsor_check_create_modal_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de sponsor: /admin/sponsor/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        sponsor_index_url = url_for('sponsor.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de sponsor
            sponsor_list_response = client.get(sponsor_index_url)
            self.assertStatus(sponsor_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            create_modal = self.get_context_variable('admin_view').create_modal
            self.assertTrue(create_modal)

    def test_admin_sponsor_check_edit_modal_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de sponsor: /admin/sponsor/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        sponsor_index_url = url_for('sponsor.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de sponsor
            sponsor_list_response = client.get(sponsor_index_url)
            self.assertStatus(sponsor_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            edit_modal = self.get_context_variable('admin_view').edit_modal
            self.assertTrue(edit_modal)

    def test_admin_sponsor_check_can_view_details_is_true(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de sponsors: /admin/sponsor/
        Verificamos:
            - que não permite editar registros
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        sponsor_index_url = url_for('sponsor.index_view')

        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de periódicos
            sponsor_list_response = client.get(sponsor_index_url)
            self.assertStatus(sponsor_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            can_view_details = self.get_context_variable('admin_view').can_view_details
            self.assertTrue(can_view_details)

    def test_admin_sponsor_check_searchable_columns(self):
        """
        Com:
            - usuário administrador cadastrado (com email confirmado)
        Quando:
            - fazemos login e
            - acessamos a pagina de listagem de sponsors: /admin/sponsor/
        Verificamos:
            - que contém todos os campos de busca esperados
        """
        # with
        admin_user = {
            'email': 'admin@opac.org',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('admin.login_view')
        sponsor_index_url = url_for('sponsor.index_view')
        expected_column_searchable_list = ('name',)
        # when
        with self.client as client:
            # login do usuario admin
            login_response = client.post(
                login_url,
                data=admin_user,
                follow_redirects=True)
            self.assertStatus(login_response, 200)
            # acesso a aba de sponsor
            sponsor_list_response = client.get(sponsor_index_url)
            self.assertStatus(sponsor_list_response, 200)
            self.assertTemplateUsed('admin/model/list.html')
            # verificamos os filtros da view
            column_searchable_list = self.get_context_variable('admin_view').column_searchable_list
            self.assertEqual(len(expected_column_searchable_list), len(column_searchable_list))
            for expected_searchable_field in expected_column_searchable_list:
                self.assertIn(expected_searchable_field, column_searchable_list)
