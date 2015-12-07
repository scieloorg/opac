# coding: utf-8

from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

from flask import current_app
import app


def get_timed_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def send_email(recipient, subject, html):
    msg = Message(subject=subject,
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[recipient, ],
                  html=html)
    app.mail.send(msg)
