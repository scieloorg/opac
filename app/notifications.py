# coding: utf-8

"""
Notificações:
    funções que enviam as notificações do sistema.
"""

from flask import url_for, render_template
import utils


def send_confirmation_email(recipient_email):
    """
    Envia um email de confirmação para 'recipient_email'
    Retorna:
     - (True, '') em caso de éxito
     - (Flase, '<MSG/EXCEPTION ERROR>') em caso de exceção/erro
    """
    try:
        ts = utils.get_timed_serializer()
        token = ts.dumps(recipient_email, salt='email-confirm-key')
    except Exception, e:
        return (False, 'Invalid Token: %s' % str(e))
    else:
        confirm_url = url_for('admin.confirm_email', token=token, _external=True)
        utils.send_email(
            recipient_email,
            "Confirm your email",
            render_template('email/activate.html', confirm_url=confirm_url))
        return (True, '')


def send_reset_password_email(recipient_email):
    """
    Envia um email com as intruccões para recuperar a senha para: 'recipient_email'
    Retorna:
     - (True, '') em caso de éxito
     - (Flase, '<MSG/EXCEPTION ERROR>') em caso de exceção/erro
    """
    try:
        ts = utils.get_timed_serializer()
        token = ts.dumps(recipient_email, salt='recover-key')
    except Exception, e:
        return (False, 'Invalid Token: %s' % str(e))
    else:
        recover_url = url_for('.reset_with_token', token=token, _external=True)
        utils.send_email(
            recipient_email,
            "Password reset requested",
            render_template('email/recover.html', recover_url=recover_url))
        return (True, '')
