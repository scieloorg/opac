# coding: utf-8

"""
    Notificações:
        Conjunto de funções que enviam as notificações do sistema.
"""

import six
from flask import render_template, url_for
from webapp.utils import utils


def send_confirmation_email(recipient_email):
    """
    Envia um email de confirmação para ``recipient_email``
    Retorna:
     - (True, '') em caso de sucesso.
     - (False, 'MENSAGEM DE ERRO/EXCEÇÃO') em caso de exceção/erro
    """
    if not isinstance(recipient_email, six.string_types) or not utils.REGEX_EMAIL.match(
        recipient_email
    ):
        raise ValueError("recipient_email é inválido!")
    try:
        ts = utils.get_timed_serializer()
        token = ts.dumps(recipient_email, salt="email-confirm-key")
    except Exception as e:
        return (False, "Token inválido: %s" % str(e))
    else:
        confirm_url = url_for("admin.confirm_email", token=token, _external=True)
        sent_results = utils.send_email(
            recipient_email,
            "Confirmação de email",
            render_template("email/activate.html", confirm_url=confirm_url),
        )
        return sent_results


def send_reset_password_email(recipient_email):
    """
    Envia um email com as intruccões para recuperar a senha para: ``recipient_email``
    Retorna:
     - (True, '') em caso de sucesso.
     - (False, 'MENSAGEM DE ERRO/EXCEÇÃO') em caso de exceção/erro
    """
    if not isinstance(recipient_email, six.string_types) or not utils.REGEX_EMAIL.match(
        recipient_email
    ):
        raise ValueError("recipient_email é inválido!")
    try:
        ts = utils.get_timed_serializer()
        token = ts.dumps(recipient_email, salt="recover-key")
    except Exception as e:
        return (False, "Token inválido: %s" % str(e))
    else:
        recover_url = url_for("admin.reset_with_token", token=token, _external=True)
        sent_results = utils.send_email(
            recipient_email,
            "Instruções para recuperar sua senha",
            render_template("email/recover.html", recover_url=recover_url),
        )

        return sent_results
