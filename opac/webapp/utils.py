# coding: utf-8

import os
import shutil
from lxml import etree
from werkzeug import secure_filename
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import current_app
import controllers
import models
import webapp
import re

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
    ImageOps = None

CSS = "/static/css/style_article_html.css"  # caminho para o CSS a ser incluído no HTML do artigo
REGEX_EMAIL = re.compile(r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", re.IGNORECASE)  # RFC 2822 (simplified)


def namegen_filename(obj, file_data=None):
    """
        Retorna um nome de arquivo seguro para o arquivo subido,
        utilizando o nome (campo "name" do modelo) e mantendo a extensão original
    """

    if isinstance(obj, basestring):
        _, extension = os.path.splitext(obj)
        return secure_filename('%s%s' % (_, extension))
    else:
        _, extension = os.path.splitext(file_data.filename)
        return secure_filename('%s%s' % (obj.name, extension))


def thumbgen_filename(filename):
    """
        Gera o nome do arquivo do thumbnail a partir do  filename.
    """
    name, ext = os.path.splitext(filename)
    return '%s_thumb%s' % (name, ext)


def get_timed_serializer():
    """
    Retorna uma instância do URLSafeTimedSerializer necessário para gerar tokens
    """
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def send_email(recipient, subject, html):
    """
    Método auxiliar para envio de emails
    - recipient: destinatario
    - subject: assunto
    - html: corpo da mensagem (formato html)
    Quem envía a mensagem é que for definido na configuração: 'MAIL_DEFAULT_SENDER'
    """
    msg = Message(subject=subject,
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[recipient, ],
                  html=html)
    webapp.mail.send(msg)


def reset_db():
    """
    Apaga todos os dados de todas as tabelas e cria novas tabelas, SEM DADOS!
    """

    webapp.dbsql.drop_all()
    webapp.dbsql.create_all()
    webapp.dbsql.session.commit()


def create_db_tables():
    """
    Cria as tabelas no banco SQL, SEM DADOS!
    """

    try:
        webapp.dbsql.create_all()
        webapp.dbsql.session.commit()
    except Exception, e:
        # TODO: melhorar o informe do erro
        raise e


def create_user(user_email, user_password, user_email_confirmed):
    """
    Cria um novo usuário, com acesso habilitado para acessar no admin.
    O parâmetro: ``user_password`` deve ser a senha em texto plano,
    que sera "hasheada" no momento de salvar o usuário.
    """

    new_user = models.User(
        email=user_email,
        password=user_password,
        email_confirmed=user_email_confirmed)
    webapp.dbsql.session.add(new_user)
    webapp.dbsql.session.commit()

    return new_user


def generate_thumbnail(input_filename):
    """
    Parâmento input_filename matriz do thumbnail.

    Caso a geração seja realizado com sucesso deve retorna o path do thumbnail,
    caso contrário None.
    """

    image_root = current_app.config['IMAGE_ROOT']

    size = (current_app.config["THUMBNAIL_HEIGHT"],
            current_app.config["THUMBNAIL_WIDTH"])

    image_path = os.path.join(image_root, thumbgen_filename(input_filename))

    try:
        img = Image.open(input_filename)
        img.thumbnail(size)
        img.save(image_path)
    except Exception as e:
        print e
    else:
        return image_path


def create_image(image_path, filename):
    """
    Função que cria uma imagem para o modelo Image.

    Parâmento image_path caminho absoluto para a imagem.
    Parâmento filename no para o arquivo com extensão.
    """

    image_root = current_app.config['IMAGE_ROOT']

    image_destiation_path = os.path.join(image_root, filename)

    shutil.copyfile(image_path, image_destiation_path)

    generate_thumbnail(image_destiation_path)

    img = models.Image(name=namegen_filename(filename), path='images/' + filename)

    webapp.dbsql.session.add(img)
    webapp.dbsql.session.commit()
