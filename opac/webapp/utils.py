# coding: utf-8

import os
from lxml import etree
import packtools
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

from unicodedata import normalize


CSS = "/static/css/style_article_html.css"  # caminho para o CSS a ser incluído no HTML do artigo
REGEX_EMAIL = re.compile(r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", re.IGNORECASE)  # RFC 2822 (simplified)

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def get_timed_serializer():
    """
    Retorna uma instância do URLSafeTimedSerializer necessário para gerar tokens
    """
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def slugify(text, delim=u''):
    """
    Generates an slightly worse ASCII-only slug.
    Originally from:
    http://flask.pocoo.org/snippets/5/
    Generating Slugs
    By Armin Ronacher filed in URLs
    """
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


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


def rebuild_article_xml(article):
    """
    Método auxilixar para regerar o HTML de um artigo, a partir do atributo xml (``article.xml``).
    Caso exista algum problema no processo, levanta a exceção.
    Caso o artigo recebido por parametro, não tenha atribute ``xml``, levanta um ValueError
    """

    if article.xml:
        try:
            htmls = []
            xml_etree = etree.ElementTree(etree.XML(article.xml.encode('utf-8')))
            html_iterator = packtools.HTMLGenerator.parse(xml_etree, valid_only=False, css=CSS)
            for lang, output in html_iterator:
                article_html_doc = controllers.new_article_html_doc(**{
                    "language": str(lang),
                    "source": etree.tostring(
                        output,
                        encoding="utf-8",
                        method="html",
                        doctype=u"<!DOCTYPE html>")
                })
                htmls.append(article_html_doc)
            article.htmls = htmls
            article.save()
        except Exception as e:
            # print "Article aid: %s, sem html, Error: %s" % (article.aid, e.message)
            raise
    else:
        raise ValueError('article.xml is None')


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


def generate_thumbnail(input_filename, thumbnail_path, size=(100, 100)):
    """
    Parâmento input_filename matrix do thumbnail.
    Parâmento thumbnail_path caminho completo para o thumbnail, o thumbnail
    terá o mesmo nome do arquivo original concatenado com '_thumb'.
    Parâmentro size tupla contendo o tamanho do thumbnail, padrão (100,100)

    Caso a geração seja realizado com sucesso deve retorna o path do thumbnail,
    caso contrário None.
    """
    name, ext = os.path.splitext(os.path.basename(input_filename))
    image_path = os.path.join(thumbnail_path, '%s_thumb%s' % (name, ext))

    try:
        img = Image.open(input_filename)
        img.thumbnail(size)
        img.save(image_path)
    except Exception as e:
        print e
    else:
        return image_path
