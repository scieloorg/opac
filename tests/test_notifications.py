# coding: utf-8

from flask import url_for, render_template
from app.notifications import send_confirmation_email, send_reset_password_email
from app import utils
from base import BaseTestCase
from mock import patch
from itsdangerous import URLSafeTimedSerializer


class NotificationsTestCase(BaseTestCase):

    def test_empty_recipient_email(self):

        recipient_email = None

        with self.assertRaises(ValueError):
            send_confirmation_email(recipient_email)

        with self.assertRaises(ValueError):
            send_reset_password_email(recipient_email)

    def test_invalid_recipient_email(self):

        recipient_email = 'foo@bar'

        with self.assertRaises(ValueError):
            send_confirmation_email(recipient_email)

        with self.assertRaises(ValueError):
            send_reset_password_email(recipient_email)

    def test_invalid_token(self):

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

            result = send_reset_password_email(recipient_email)
            self.assertEqual(expected, result)

    def test_send_confirmation_email(self):

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
