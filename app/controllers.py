# coding: utf-8

"""
    Conjunto de funções utilitarias para acessar a camada de modelos,
    e agrupar esses resultados em estruturas de dados úties para as views
    ou outras camadas superiores, evitando assim que as camadas superiores
    acessem diretamente a camada inferior de modelos.
"""

import datetime
from opac_schema.v1.models import Journal, Issue, Article, ArticleHTML
from flask import current_app
from app import dbsql
from . import models as sql_models


# -------- JOURNAL --------

def get_journals(collection=None, is_public=True, order_by="title"):
    """
    Retorna uma lista de periódicos considerando os parâmetros:
    - ``collection``: acrônimo da coleção, caso seja None filtra
                      pelo acrônimo definido na configuração OPAC_COLLECTION;
    - ``is_public``: filtra por público e não público de cada periódico;
    - ``order_by``: que corresponde ao nome de um atributo pelo qual
                    deve estar ordenada a lista resultante.
    """

    if not collection:
        collection = current_app.config.get('OPAC_COLLECTION')

    return Journal.objects(is_public=is_public).order_by(order_by)


def get_journals_by_study_area():
    """
    Retorna dicionário com 2 chaves: ``meta`` e ``objects``.

    - ``meta`` é um dicionario de metadados, que contém o ``total`` de periódicos retornados;
    - ``objects`` é um dicionario de periódicos agrupados pela área de conhecimento.

    Exemplo:
    ```
    {
        'meta': {'total':4},
        'objects': {
            'Health Sciences': [<Journal: aiss>, <Journal: bwho>],
            'Engineering': [<Journal: ICSE>, <Journal: csp>]
        }
    }
    ```
    """

    journals = get_journals()

    dict_journals = {}

    meta = {
        'total': len(journals),
    }

    for journal in journals:
        for area in journal.study_areas:
            dict_journals.setdefault(area, []).append(journal)

    return {'meta': meta, 'objects': dict_journals}


def get_journals_by_indexer():
    """
    Retorna dicionário com 2 chaves: ``meta`` e ``objects``.

    - ``meta`` é um dicionario de metadados, que contem o ``total`` de periódicos retornados;
    - ``objects`` é um dicionario de periódicos agrupados pelo indexador.

    Exemplo:
    ```
    {
        'meta': {'total':4},
        'objects': {
            'SCIE': [<Journal: aiss>, <Journal: bwho>],
            'SSCI': [<Journal: ICSE>, <Journal: csp>]
        }
    }
    ```
    """

    journals = get_journals()

    dict_journals = {}

    meta = {
        'total': len(journals),
    }

    for journal in journals:
        for indexer in journal.index_at:
            dict_journals.setdefault(indexer, []).append(journal)

    return {'meta': meta, 'objects': dict_journals}


def get_journals_by_sponsor():
    """
    Retorna dicionário com 2 chaves: ``meta`` e ``objects``.

    - ``meta`` é um dicionario de metadados, que contem o ``total`` de periódicos retornados;
    - ``objects`` é um dicionario de periódicos agrupados pelo patrocinador.

    Exemplo:
    ```
    {
        'meta': {'total':4},
        'objects': {
            'World Health Organization': [<Journal: aiss>, <Journal: bwho>],
            'The Atlantic Philanthropies': [<Journal: ICSE>, <Journal: csp>]
        }
    }
    ```
    """

    journals = get_journals()

    dict_journals = {}

    meta = {
        'total': len(journals),
    }

    for journal in journals:
        for indexer in journal.sponsors:
            dict_journals.setdefault(indexer, []).append(journal)

    return {'meta': meta, 'objects': dict_journals}


def get_journal_by_jid(jid, is_public=True):
    """
    Retorna um periódico considerando os parâmetros ``jid`` e ``is_public``

    - ``jid``: string, chave primaria do periódico (ex.: ``f8c87833e0594d41a89fe60455eaa5a5``);
    - ``is_public``: boolean, filtra por público e não público.
    """

    return Journal.objects(jid=jid, is_public=is_public).first()


def get_journals_by_jid(jids):
    """
    Retorna uma lista de periódicos aonde o atributo ``jid`` de cada um deles
    pertence a lista do parâmetro: ``jids``

    - ``jids``: lista de jids de periódicos a serem filtrados.
    """

    return Journal.objects.in_bulk(jids)


def set_journal_is_public_bulk(jids, is_public=True):
    """
    Atualiza uma lista de periódicos como público ou não público.

    - ``jids``: lista de jids de periódicos a serem atualizados.
    - ``is_public``: boolean, filtra por público e não público.
    """
    for journal in get_journals_by_jid(jids).values():
        journal.is_public = is_public
        journal.save()


# -------- ISSUE --------

def get_issues_by_jid(jid, is_public=True, order_by=None):
    """
    Retorna uma lista de fascículos considerando os parâmetros ``jid`` e ``is_public``,
    e ordenado por parâmetro ``order_by``.

    - ``jid``: string, chave primaria do periódico (ex.: ``f8c87833e0594d41a89fe60455eaa5a5``);
    - ``is_public``: boolean, filtra por público e não público.
    - ``order_by``: string ou lista, campo ou lista de campos para fazer a ordenação.
    """

    if not order_by:
        order_by = ["-year", "-volume", "-number"]

    if get_journal_by_jid(jid):
        return Issue.objects(journal=jid, is_public=True).order_by(*order_by)


def get_issue_by_iid(iid, is_public=True):
    """
    Retorna um fascículo considerando os parâmetros ``iid`` e ``is_public``.

    - ``iid``: string, chave primaria do fascículo (ex.: ``f8c87833e0594d41a89fe60455eaa5a5``);
    - ``is_public``: boolean, filtra por público e não público.
    """

    issue = Issue.objects.filter(iid=iid).first()

    if issue.journal.is_public == is_public and issue.is_public == is_public:
        return issue


def get_issues_by_iid(iids):
    """
    Retorna uma lista de fascículos aonde o atributo ``iid`` de cada um deles
    pertence a lista do parâmetro: ``iids``

    - ``iids``: lista de iids de fascículos a serem filtrados.
    """

    return Issue.objects.in_bulk(iids)


def set_issue_is_public_bulk(iids, is_public=True):
    """
    Atualiza uma lista de fascículos como público ou não público.

    - ``iids``: lista de iids de fascículos a serem atualizados.
    - ``is_public``: boolean, filtra por público e não público.
    """

    for issue in get_issues_by_iid(iids).values():
        issue.is_public = is_public
        issue.save()


# -------- ARTICLE --------

def get_article_by_aid(aid, is_public=True):
    """
    Retorna um artigo considerando os parâmetros ``aid`` e ``is_public``.

    - ``aid``: string, chave primaria do artigo (ex.: ``14a278af8d224fa2a09a901123ca78ba``);
    - ``is_public``: boolean, filtra por público e não público.
    """

    article = Article.objects(aid=aid).first()

    article_public = article.is_public
    journal_public = article.journal.is_public
    issue_public = article.issue.is_public

    if all([article_public, journal_public, issue_public]):
        return article


def get_articles_by_aid(aids):
    """
    Retorna uma lista de artigos aonde o atributo ``aid`` de cada um deles
    pertence a lista do parâmetro: ``aids``

    - ``aids``: lista de aids de artigos a serem filtrados.
    """

    return Article.objects.in_bulk(aids)


def set_article_is_public_bulk(aids, is_public=True):
    """
    Atualiza uma lista de artigos como público ou não público.

    - ``aids``: lista de aids de artigos a serem atualizados.
    - ``is_public``: boolean, filtra por público e não público.
    """

    for article in get_articles_by_aid(aids).values():
        article.is_public = is_public
        article.save()


def get_articles_by_iid(iid, is_public=True):
    """
    Retorna uma lista de artigos aonde o atributo ``iid`` de cada um deles
    é igual ao parâmetro: ``iid``.

    - ``iid``: chave primaria de fascículo para escolher os artigos.
    """

    return Article.objects(issue=iid, is_public=is_public)

# -------- SLQALCHEMY --------


def get_user_by_email(email):
    """
    Retorna o usuário aonde seu atributo ``email`` é igual ao parâmetro ``email``.
    """
    return dbsql.session.query(sql_models.User).filter_by(email=email).first()


def get_user_by_id(id):
    """
    Retorna o usuário aonde seu atributo ``id`` é igual ao parâmetro ``id``.
    """
    return dbsql.session.query(sql_models.User).get(id)


def set_user_email_confirmed(user):
    """
    Atualiza o usuário ``user`` deixando ele com email confirmado (atributo ``email_confirmed`` = True).
    """
    user.email_confirmed = True
    dbsql.session.add(user)
    dbsql.session.commit()


def set_user_password(user, password):
    """
    Atualiza o usuário ``user`` com a senha definida pelo parâmetro ``password``.
    """
    user.password = password
    dbsql.session.add(user)
    dbsql.session.commit()


def filter_articles_by_ids(ids):
    """
    Retorna uma lista de artigos aonde o atributo ``iid`` de cada um deles
    pertence a lista do parâmetro: ``iids``

    - ``iids``: lista de iids de fascículos a serem filtrados.
    """
    return Article.objects(_id__in=ids)


def new_article_html_doc(language, source):
    """
    Retorna uma nova instância de ArticleHTML com os atributos definidos pelos parâmetros:
    - ``language`` o código de idioma do artigos;
    - ``source`` a string como o HTML do artigos.
    """
    return ArticleHTML(language=language, source=source)


def count_elements_by_type_and_visibility(type, public_only=False):
    """
    Retorna a quantidade de registros indicado pelo @type.
    @params:
    - ``type``: O tipo de elemento que queremos contabilizar.
                Deve ser "journal" ou "issue" ou "article";
    - ``public_only``: Se for True, filtra na contagem somente os registros públicos,
                       caso contrario contabliza todos (públicos e não publicos);
    """

    if type == 'journal':
        if public_only:
            return Journal.objects(is_public=True).count()
        else:
            return Journal.objects.count()
    elif type == 'issue':
        if public_only:
            return Issue.objects(is_public=True).count()
        else:
            return Issue.objects.count()
    elif type == 'article':
        if public_only:
            return Article.objects(is_public=True).count()
        else:
            return Article.objects.count()
    else:
        raise ValueError(u"Parâmetro 'type' errado, tente: 'journal' ou 'issue' ou 'article'.")
