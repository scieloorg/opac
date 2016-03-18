# coding: utf-8

from lxml import etree
import packtools
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import current_app
from . import dbsql, controllers, mail, models

CSS = "/static/css/style_article_html.css"  # caminho para o CSS a ser incluído no HTML do artigo


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
    mail.send(msg)


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

    dbsql.drop_all()
    dbsql.create_all()
    dbsql.session.commit()


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
    dbsql.session.add(new_user)
    dbsql.session.commit()

    return new_user
