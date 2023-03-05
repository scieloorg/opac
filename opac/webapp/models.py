# coding: utf-8

"""
    Conjunto de modelos relacionais para o controle da app (Usuarios, auditorias, logs, etc)
    Os modelos do catálogo do OPAC (periódicos, números, artigos) estão definidos na
    lib: opac_schema (ver requirements.txt)
"""

import os

from flask import current_app
from flask_login import UserMixin
from sqlalchemy.event import listens_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils.types.choice import ChoiceType
from webapp.utils import thumbgen_filename
from werkzeug.security import check_password_hash, generate_password_hash

from . import dbsql as db
from . import login_manager, notifications

LANGUAGES_CHOICES = [
    ("pt", "Português"),
    ("en", "English"),
    ("es", "Español"),
]


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    _password = db.Column(
        db.String(128), nullable=True
    )  # deve ser possível add novo user sem setar senha
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = generate_password_hash(plaintext)

    def define_password(self, plaintext):
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
            raise ValueError("Usuário deve ter email válido para realizar o envío")
        else:
            return notifications.send_confirmation_email(self.email)

    def send_reset_password_email(self):
        if not self._check_valid_email():
            raise ValueError("Usuário deve ter email válido para realizar o envío")
        else:
            return notifications.send_reset_password_email(self.email)

    def _check_valid_email(self):
        """
        retorna True quando a instância (self) do usuário, tem um email válido.
        retorna False em outro caso.
        """
        from webapp.admin.forms import EmailForm

        if not self.email or self.email == "" or self.email == "":
            return False
        else:
            form = EmailForm(data={"email": self.email})
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


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), nullable=False)
    path = db.Column(db.Unicode(256), nullable=False)
    language = db.Column(ChoiceType(LANGUAGES_CHOICES), nullable=True)

    def __unicode__(self):
        return self.name

    @property
    def get_absolute_url(self):
        media_url = current_app.config["MEDIA_URL"]
        return "%s/%s" % (media_url, self.path)


# Delete hooks: remove arquivos quando o modelo é apagado
@listens_for(File, "after_delete")
def delelte_file_hook(mapper, connection, target):
    if target.path:
        media_root = current_app.config["MEDIA_ROOT"]
        try:
            os.remove(os.path.join(media_root, target.path))
        except OSError:
            pass  # Se der erro não importa, o arquivo já não existe


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), nullable=False)
    path = db.Column(db.Unicode(256), nullable=False)
    language = db.Column(ChoiceType(LANGUAGES_CHOICES), nullable=True)

    def __unicode__(self):
        return self.name

    @property
    def get_absolute_url(self):
        media_url = current_app.config["MEDIA_URL"]
        return "%s/%s" % (media_url, self.path)

    @property
    def get_thumbnail_absolute_url(self):
        media_url = current_app.config["MEDIA_URL"]
        thumb_path = thumbgen_filename(self.path)
        return "%s/%s" % (media_url, thumb_path)


# Delete hooks: remove arquivos quando o modelo é apagado
@listens_for(Image, "after_delete")
def delelte_image_hook(mapper, connection, target):
    if target.path:
        media_root = current_app.config["MEDIA_ROOT"]
        # Remover a imagem
        try:
            os.remove(os.path.join(media_root, target.path))
        except OSError:
            pass  # Se der erro não importa, o arquivo já não existe

        # Remover o thumbnail
        try:
            thumb_path = thumbgen_filename(target.path)
            os.remove(os.path.join(media_root, thumb_path))
        except OSError:
            pass  # Se der erro não importa, o arquivo já não existe
