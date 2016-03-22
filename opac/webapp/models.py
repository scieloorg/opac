# coding: utf-8

"""
    Conjunto de modelos relacionais para o controle da app (Usuarios, auditorias, logs, etc)
    Os modelos do catálogo do OPAC (periódicos, fascículos, artigos) estão definidos na
    lib: opac_schema (ver requirements.txt)
"""

from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from . import dbsql as db
from . import login_manager
import notifications


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    _password = db.Column(db.String(128), nullable=True)  # deve ser possível add novo user sem setar senha
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        """
        Compara a string ``plaintext`` com a senha "hasheada" armazenada para este usuário.
        """
        if not self._password:
            return False
        else:
            return check_password_hash(self._password, plaintext)

    def send_confirmation_email(self):
        if not self._check_valid_email():
            raise ValueError(u'Usuário deve ter email válido para realizar o envío')
        else:
            return notifications.send_confirmation_email(self.email)

    def send_reset_password_email(self):
        if not self._check_valid_email():
            raise ValueError(u'Usuário deve ter email válido para realizar o envío')
        else:
            return notifications.send_reset_password_email(self.email)

    def _check_valid_email(self):
        """
        retorna True quando a instância (self) do usuário, tem um email válido.
        retorna False em outro caso.
        """
        from webapp.admin.forms import EmailForm
        if not self.email or self.email == '' or self.email == u'':
            return False
        else:
            form = EmailForm(data={'email': self.email})
            return form.validate()

    # Required for administrative interface
    def __unicode__(self):
        return self.email


@login_manager.user_loader
def load_user(user_id):
    """
        Retora usuário pelo id.
        Necessário para o login manager.
    """
    return User.query.get(int(user_id))
