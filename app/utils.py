# coding: utf-8
from lxml import etree
import packtools
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import current_app
import app

CSS = "/static/css/style_article_html.css"


def get_timed_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def send_email(recipient, subject, html):
    msg = Message(subject=subject,
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[recipient, ],
                  html=html)
    app.mail.send(msg)


def rebuild_article_xml(article):
    import controllers  # WTF? top level não funciona
    if article.xml:
        try:
            htmls = []
            xml_etree = etree.ElementTree(etree.XML(article.xml.encode('utf-8')))
            # xml_etree = etree.XML(article.xml.encode('utf-8'))
            # xml_string = StringIO(article.xml.encode('utf-8'))
            html_iterator = packtools.HTMLGenerator(xml_etree, valid_only=False, css=CSS)
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
