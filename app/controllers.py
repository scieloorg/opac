# coding: utf-8

import datetime
from opac_schema.v1.models import Journal, Issue, Article, ArticleHTML
from flask import current_app
from app import dbsql
from . import models as sql_models


# -------- JOURNAL --------

def get_journals_alpha(collection=None, is_public=True, order_by="title"):
    """
    Retorna uma coleção de periódicos considerando os atributos ``collection``,
    ``is_public``, ordenado pelo parâmetro ``order_by``.

    @param collection: string, caso None utiliza o valor do arquivo de configuraçõa
    OPAC_COLLECTION.
    @param is_public: boolean, filtra por público e não público.
    @param order_by: string, atributo para ordenar.
    """
    if not collection:
        collection = current_app.config.get('OPAC_COLLECTION')

    return Journal.objects(collections__acronym=collection,
                           is_public=is_public).order_by(order_by)


def get_journal_by_jid(jid, is_public=True):
    """
    Retorna um periódico considerando os parâmetros ``jid`` e ``is_public``

    @param jid: string, ex.: ``f8c87833e0594d41a89fe60455eaa5a5``.
    @param is_public: boolean, filtra por público e não público.
    """
    return Journal.objects(jid=jid, is_public=is_public).first()


def get_journals_by_jid(jids):
    """
    Retorna uma coleção de periódicos.

    @param jids: list or set de ids do periódico.
    """
    return Journal.objects.in_bulk(jids)


def set_journal_is_public_bulk(jids, is_public=True):
    """
    Marca uma lista de periódicos como público ou não público.

    @param jids: list ou set de ids do periódico.
    @param is_public: boolean, filtra por público e não público.
    """
    for journal in get_journals_by_jid(jids).values():
        journal.is_public = is_public
        journal.save()


# -------- ISSUE --------

def get_issues_by_jid(jid, is_public=True, order_by=None):
    """
    Retorna fascículos pelo parâmetro ``jid``, ordenado por ``order_by``

    @param jid: string, ex.: ``f8c87833e0594d41a89fe60455eaa5a5``.
    @param order_by: string, atributo para ordenar.
    """
    if not order_by:
        order_by = ["-year", "-volume", "-number"]

    if get_journal_by_jid(jid):
        return Issue.objects(journal=jid, is_public=True).order_by(*order_by)


def get_issue_by_iid(iid, is_public=True):
    """
    Retorna um fascículo filtrando pela chave ``iid``, com a condição que o
    periódico e o fascículo satisfaça o valor boleano do parâmetro
    ``is_public``.

    @param iid: string, ex.: ``f8c87833e0594d41a89fe60455eaa5a5``.
    @param is_public: boolean, filtra por público e não público.
    """
    issue = Issue.objects.filter(iid=iid).first()

    if issue.journal.is_public == is_public and issue.is_public == is_public:
        return issue


def get_issues_by_iid(iids):
    """
    Retorna uma coleção de fascículos.

    @param jids: list ou set de iids de fascículos.
    """
    return Issue.objects.in_bulk(iids)


def set_issue_is_public_bulk(iids, is_public=True):
    """
    Marca uma lista de fascículos como público ou não público.

    @param iids: list ou set de ids de fascículos.
    @param is_public: boolean.
    """
    for issue in get_issues_by_iid(iids).values():
        issue.is_public = is_public
        issue.save()


# -------- ARTICLE --------

def get_article_by_aid(aid, is_public=True):
    """
    Retorna um artigo considerando o parâmetro ``aid`` e ``is_public``, com a
    condição que o periódico e o fascículos dessa artigo também satisfaça o
    valor boleano do parâmetro ``is_public``.

    @param aid: string, ex.: ``14a278af8d224fa2a09a901123ca78ba``.
    @param is_public: boolean, filtra por público e não público.
    """
    article = Article.objects(aid=aid).first()

    article_public = article.is_public
    journal_public = article.journal.is_public
    issue_public = article.issue.is_public

    if all([article_public, journal_public, issue_public]):
        return article


def get_articles_by_aid(aids):
    """
    Retorna uma artigos filtrando pelo parâmetro ``aids``.

    @param aids: list or set de aids.
    """
    return Article.objects.in_bulk(aids)


def set_article_is_public_bulk(aids, is_public=True):
    """
    Marca uma lista de artigos como público ou não público.

    @param iids: list ou set de aids.
    @param is_public: boolean.
    """
    for article in get_articles_by_aid(aids).values():
        article.is_public = is_public
        article.save()


def get_articles_by_iid(iid, is_public=True):
    """
    Retorna artigos filtrando pelo ``iid`` do fascículo.
    """
    return Article.objects(issue=iid, is_public=is_public)

# -------- SLQALCHEMY --------


def get_user_by_email(email):
    return dbsql.session.query(sql_models.User).filter_by(email=email).first()


def get_user_by_id(id):
    return dbsql.session.query(sql_models.User).get(id)


def set_user_email_confirmed(user):
    user.email_confirmed = True
    dbsql.session.add(user)
    dbsql.session.commit()


def set_user_password(user, password):
    user.password = password
    dbsql.session.add(user)
    dbsql.session.commit()


def filter_articles_by_ids(ids):
    return Article.objects(_id__in=ids)


def new_article_html_doc(language, source):
    return ArticleHTML(language=language, source=source)
