# coding: utf-8

from flask_babelex import gettext as _
from wtforms import form, fields, validators
from app.controllers import get_user_by_email


class LoginForm(form.Form):
    email = fields.TextField(_(u'Email'), validators=[validators.required(), validators.email()])
    password = fields.PasswordField(_(u'Senha'), validators=[validators.required()])

    def validate_password(self, field):
        user = get_user_by_email(self.email.data)
        if user is None:
            raise validators.ValidationError(_(u'Usuário inválido'))
        if not user.is_correct_password(self.password.data):
            raise validators.ValidationError(_(u'Senha inválida'))


class EmailForm(form.Form):
    email = fields.TextField(_(u'Email'), validators=[validators.required(), validators.email()])


class PasswordForm(form.Form):
    password = fields.PasswordField(_(u'Senha'), validators=[validators.required()])
