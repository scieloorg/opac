# coding: utf-8

from flask import url_for, render_template
from webapp.notifications import send_confirmation_email, send_reset_password_email
from webapp import utils
from .base import BaseTestCase
from mock import patch
from itsdangerous import URLSafeTimedSerializer


class NotificationsTestCase(BaseTestCase):

    def test_send_confirmation_email_with_empty_recipient_email(self):
        """
        Com:
            - recipient_email = None
        Quando:
            - Enviamos notificações de confiração de email
        Verificamos:
            - Que ocorra uma exeção por causa do email inválido para recipient_email
        """

        recipient_email = None

        with self.assertRaises(ValueError):
            send_confirmation_email(recipient_email)

    def test_send_reset_password_email_with_empty_recipient_email(self):
        """
        Com:
            - recipient_email = None
        Quando:
            - Enviamos notificações de resetar a senha
        Verificamos:
            - Que ocorra uma exeção por causa do email inválido para recipient_email
        """

        recipient_email = None

        with self.assertRaises(ValueError):
            send_reset_password_email(recipient_email)

    def test_send_confirmation_email_with_invalid_recipient_email(self):
        """
        Com:
            - recipient_email inválido
        Quando:
            - Enviamos notificações de confirmación de email
        Verifcamos:
            - Que ocorra uma exeção por causa do email inválido para recipient_email
        """

        recipient_email = 'foo@bar'

        with self.assertRaises(ValueError):
            send_confirmation_email(recipient_email)

    def test__send_reset_password_email_with_invalid_recipient_email(self):
        """
        Com:
            - recipient_email inválido
        Quando:
            - Enviamos notificações de resetar a senha
        Verifcamos:
            - Que ocorra uma exeção por causa do email inválido para recipient_email
        """

        recipient_email = 'foo@bar'

        with self.assertRaises(ValueError):
            send_reset_password_email(recipient_email)

    def test_invalid_token_confirmation_email(self):
        """
        Quando:
            - current_app.config["SECRET_KEY"] não tem valor
        Verifcamos:
            - Que ocorra uma exeção qunado é criado um token com
              get_timed_serializer ao enviar a notificação de confirmação de email.
        """

        recipient_email = 'foo@bar.baz'

        with patch('webapp.utils.get_timed_serializer') as mock:
            mock.return_value = URLSafeTimedSerializer(None)

            expected = None
            try:
                ts = utils.get_timed_serializer()
                ts.dumps(recipient_email)
            except Exception as e:
                expected = (False, 'Token inválido: %s' % str(e))

            result = send_confirmation_email(recipient_email)
            self.assertEqual(expected, result)

    def test_invalid_token_reset_password(self):
        """
        Quando:
            - current_app.config["SECRET_KEY"] não tem valor
        Verifcamos:
            - Que ocorra uma exeção qunado é criado um token com
              get_timed_serializer ao enviar a notificação de resetar a senha.
        """

        recipient_email = 'foo@bar.baz'

        with patch('webapp.utils.get_timed_serializer') as mock:
            mock.return_value = URLSafeTimedSerializer(None)

            expected = None
            try:
                ts = utils.get_timed_serializer()
                ts.dumps(recipient_email)
            except Exception as e:
                expected = (False, 'Token inválido: %s' % str(e))

            result = send_reset_password_email(recipient_email)
            self.assertEqual(expected, result)

    def test_send_confirmation_email(self):
        """
        Com:
            - Um email válido para: recipient_email = 'foo@bar.baz'
        Quando:
            - Enviamos a notificação de confirmação de email.
        Verificamos:
            - Que ``app.utils.send_email`` seja invocado como os parámetros:
                - recipient = 'foo@bar.baz'
                - subject =   "Confirmação de email"
                - html = render_template('email/activate.html', confirm_url=confirm_url)
            - Que o valor de retorno da função: send_confirmation_email seja: (True, '')
        """

        recipient_email = 'foo@bar.baz'
        ts = utils.get_timed_serializer()
        token = ts.dumps(recipient_email, salt='email-confirm-key')
        confirm_url = url_for('admin.confirm_email', token=token, _external=True)
        result_expected = (True, '')

        with patch('webapp.utils.send_email', return_value=result_expected) as mock:

            result = send_confirmation_email(recipient_email)
            mock.assert_called_with(
                recipient_email,
                "Confirmação de email",
                render_template('email/activate.html', confirm_url=confirm_url)
            )

            self.assertEqual(result_expected, result)

    def test_send_reset_password_email(self):
        """
        Com:
            - Um email válido para: recipient_email = 'foo@bar.baz'
        Quando:
            - Enviamos a notificação de resetar a senha.
        Verificamos:
            - Que ``app.utils.send_email`` seja invocado como os parámetros:
                - recipient = 'foo@bar.baz'
                - subject =   "Instruções para recuperar sua senha"
                - html = render_template('email/recover.html', recover_url=recover_url)
            - Que o valor de retorno da função: send_confirmation_email seja: (True, '')
        """

        recipient_email = 'foo@bar.baz'
        ts = utils.get_timed_serializer()
        token = ts.dumps(recipient_email, salt='recover-key')
        recover_url = url_for('admin.reset_with_token', token=token, _external=True)
        result_expected = (True, '')

        with patch('webapp.utils.send_email', return_value=result_expected) as mock:

            result = send_reset_password_email(recipient_email)

            mock.assert_called_with(
                recipient_email,
                "Instruções para recuperar sua senha",
                render_template('email/recover.html', recover_url=recover_url)
            )

            self.assertEqual(result_expected, result)
