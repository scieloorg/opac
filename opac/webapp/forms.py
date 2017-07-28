# coding: utf-8

import re
from flask_wtf import FlaskForm
from flask_babelex import gettext as _
from wtforms import StringField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, URL, ValidationError


class EmailShareForm(FlaskForm):
    your_email = StringField('your_email', validators=[DataRequired(), Email()])
    recipients = StringField('recipients', validators=[DataRequired()])
    share_url = HiddenField('share_url', validators=[URL(), DataRequired()])
    subject = StringField('subject')
    comment = TextAreaField('comment')

    def validate_recipients(form, field):
        regex = re.compile(r'^.+@([^.@][^@]+)$', re.IGNORECASE)

        splitted_emails = field.data.split(';')

        for email in splitted_emails:
            email = email.strip()

            if email:
                match = regex.match(email or '')

                if not match:
                    raise ValidationError(_('Endereço de e-mail inválido.'))
