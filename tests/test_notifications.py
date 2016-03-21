# coding: utf-8

from flask import url_for, render_template
from app.notifications import send_confirmation_email, send_reset_password_email
from app import utils
from base import BaseTestCase
from mock import patch
from itsdangerous import URLSafeTimedSerializer


class NotificationsTestCase(BaseTestCase):

    def test_empty_recipient_email(self):
        """
        Com:
            - recipient_email = None
        Quando:
            - Enviamos notificaciones de confirmación y cambio de contraseña
        Verificamos:
            - Que ocurra una excepción por un valor incorrecto para recipient_email
        """

        recipient_email = None

        with self.assertRaises(ValueError):
            send_confirmation_email(recipient_email)

        with self.assertRaises(ValueError):
            send_reset_password_email(recipient_email)

    def test_invalid_recipient_email(self):
        """
        Com:
            - recipient_email no valido 
        Quando:
            - Enviamos notificaciones de confirmación y cambio de contraseña
        Verifcamos:
            - Que ocurra una excepción por un valor incorrecto para recipient_email
        """

        recipient_email = 'foo@bar'

        with self.assertRaises(ValueError):
            send_confirmation_email(recipient_email)

        with self.assertRaises(ValueError):
            send_reset_password_email(recipient_email)

    def test_invalid_token_confirmation_email(self):
        """
        Quando:
            - current_app.config["SECRET_KEY"] no tiene un valor
        Verifcamos:
            - Que ocurra una excepción al crear un token con get_timed_serializer
              al enviar notificación de confirmación
        """

        recipient_email = 'foo@bar.baz'

        with patch('app.utils.get_timed_serializer') as mock:
            mock.return_value = URLSafeTimedSerializer(None)

            expected = None
            try:
                ts = utils.get_timed_serializer()
                ts.dumps(recipient_email)
            except Exception, e:
                expected = (False, 'Invalid Token: %s' % str(e))

            result = send_confirmation_email(recipient_email)
            self.assertEqual(expected, result)


    def test_invalid_token_reset_password(self):
        """
        Quando:
            - current_app.config["SECRET_KEY"] no tiene un valor
        Verifcamos:
            - Que ocurra una excepción al crear un token con get_timed_serializer
              al enviar notificación para cambio de contraseña
        """

        recipient_email = 'foo@bar.baz'

        with patch('app.utils.get_timed_serializer') as mock:
            mock.return_value = URLSafeTimedSerializer(None)

            expected = None
            try:
                ts = utils.get_timed_serializer()
                ts.dumps(recipient_email)
            except Exception, e:
                expected = (False, 'Invalid Token: %s' % str(e))

            result = send_reset_password_email(recipient_email)
            self.assertEqual(expected, result)

    def test_send_confirmation_email(self):
        """
        Com:
            - Un valor correcto para: recipient_email = 'foo@bar.baz'
        Quando:
            - Enviamos notificación de confirmación
        Verificamos:
            - Que ``app.utils.send_email`` se llamado con los parámetros
            - recipient = 'foo@bar.baz'
            - subject =   "Confirmação de email"
            - html = render_template('email/activate.html', confirm_url=confirm_url)
            - que el valor de retorno para send_confirmation_email sea: (True, '')
        """

        recipient_email = 'foo@bar.baz'
        ts = utils.get_timed_serializer()
        token = ts.dumps(recipient_email, salt='email-confirm-key')
        confirm_url = url_for('admin.confirm_email', token=token, _external=True)

        with patch('app.utils.send_email') as mock:

            result = send_confirmation_email(recipient_email)
            expected = (True, '')

            mock.assert_called_with(
                recipient_email,
                "Confirmação de email",
                render_template('email/activate.html', confirm_url=confirm_url)
            )

            self.assertEqual(expected, result)

    def test_send_reset_password_email(self):
        """
        Com:
            - Un valor correcto para: recipient_email = 'foo@bar.baz'
        Quando:
            - Enviamos notificación de cambio de contraseña
        Verificamos:
            - Que ``app.utils.send_email`` se llamado con los parámetros
            - recipient = 'foo@bar.baz'
            - subject =   "Instruções para recuperar sua senha"
            - html = render_template('email/recover.html', recover_url=recover_url)
            - que el valor de retorno para send_confirmation_email sea: (True, '')
        """

        recipient_email = 'foo@bar.baz'
        ts = utils.get_timed_serializer()
        token = ts.dumps(recipient_email, salt='recover-key')
        recover_url = url_for('admin.reset_with_token', token=token, _external=True)

        with patch('app.utils.send_email') as mock:

            result = send_reset_password_email(recipient_email)
            expected = (True, '')

            mock.assert_called_with(
                recipient_email,
                "Instruções para recuperar sua senha",
                render_template('email/recover.html', recover_url=recover_url)
            )

            self.assertEqual(expected, result)
