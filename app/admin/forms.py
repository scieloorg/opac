# coding: utf-8

from wtforms import form, fields, validators

from app.controllers import get_user_by_email


class LoginForm(form.Form):
    email = fields.TextField('Email', validators=[validators.required(), validators.email()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_password(self, field):
        user = get_user_by_email(self.email.data)
        if user is None:
            raise validators.ValidationError('Invalid user')
        if not user.is_correct_password(self.password.data):
            raise validators.ValidationError('Invalid password')


class EmailForm(form.Form):
    email = fields.TextField('Email', validators=[validators.required(), validators.email()])


class PasswordForm(form.Form):
    password = fields.PasswordField('Password', validators=[validators.required()])
