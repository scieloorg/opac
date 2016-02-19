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
from flask_babelex import lazy_gettext as __
from app import dbsql
from . import models as sql_models


# -------- JOURNAL --------

def get_journals(is_public=True, order_by="title"):
    """
    Retorna uma lista de periódicos considerando os parâmetros:
    - ``is_public``: filtra por público e não público de cada periódico;
    - ``order_by``: que corresponde ao nome de um atributo pelo qual
                    deve estar ordenada a lista resultante.
    """

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


def get_journal_by_jid(jid, **kwargs):
    """
    Retorna um periódico considerando os parâmetros ``jid`` e ``kwargs``

    - ``jid``: string, chave primaria do periódico (ex.: ``f8c87833e0594d41a89fe60455eaa5a5``);
    - ``kwargs``: parâmetros de filtragem.

    Em caso de não existir itens retorna {}.
    """

    if not jid:
        raise ValueError(__(u'Obrigatório um jid.'))

    return Journal.objects(jid=jid, **kwargs).first()


def get_journals_by_jid(jids):
    """
    Retorna um dicionário de periódicos aonde o atributo ``jid`` de cada um deles
    pertence a lista do parâmetro: ``jids``

    - ``jids``: lista de jids de periódicos a serem filtrados.

    Em caso de não existir itens retorna {}.

    Exemplo do retorno:
        {
            u'jid12': <Journal: rev-jid12>,
            u'jid1': <Journal: rev-jid1>,
            u'jid123': <Journal: rev-jid123>
        }

    """

    journals = Journal.objects.in_bulk(jids)

    return journals


def set_journal_is_public_bulk(jids, is_public=True, reason=''):
    """
    Atualiza uma lista de periódicos como público ou não público.
    - ``jids``: lista de jids de periódicos a serem atualizados, caso seja,
    lista vazia retorna um ValueError.
    - ``is_public``: boolean, filtra por público e não público.
    - ``reason``: string, indica o motivo pelo qual o periódico é despublicado.
    """

    if not jids:
        raise ValueError(__(u'Obrigatório uma lista de ids.'))

    for journal in get_journals_by_jid(jids).values():
        journal.is_public = is_public
        journal.unpublish_reason = reason
        journal.save()


# -------- ISSUE --------

def get_issues_by_jid(jid, **kwargs):
    """
    Retorna uma lista de fascículos considerando os parâmetros ``jid`` e ``kwargs``,
    e ordenado por parâmetro ``order_by``.

    - ``jid``: string, chave primaria do periódico (ex.: ``f8c87833e0594d41a89fe60455eaa5a5``);
    - ``kwargs``: parâmetros de filtragem, utilize a chave ``order_by` para indicar
    uma lista de ordenação.
    """

    order_by = kwargs.get('order_by', None)

    if order_by:
        del kwargs['order_by']
    else:
        order_by = ["-year", "-volume", "-number"]

    if get_journal_by_jid(jid):
        return Issue.objects(journal=jid, **kwargs).order_by(*order_by)


def get_issue_by_iid(iid, **kwargs):
    """
    Retorna um fascículo considerando os parâmetros ``iid`` e ``kwargs``.

    - ``iid``: string, chave primaria do fascículo (ex.: ``f8c87833e0594d41a89fe60455eaa5a5``);
    - ``kwargs``: parâmetros de filtragem.
    """

    if not iid:
        raise ValueError(__(u'Obrigatório um iid.'))

    return Issue.objects.filter(iid=iid, **kwargs).first()


def get_issues_by_iid(iids):
    """
    Retorna um dicionário de fascículos aonde o atributo ``iid`` de cada um deles
    pertence a lista do parâmetro: ``iids``

    - ``iids``: lista de iids de fascículos a serem filtrados.

    Em caso de não existir itens retorna {}.

    Exemplo do retorno:
        {
            u'iid12': <Issue: issue-iid12>,
            u'iid1': <Issue: issue-iid1>,
            u'iid123': <Issue: issue-iid123>
        }
    """

    issues = Issue.objects.in_bulk(iids)

    return issues


def set_issue_is_public_bulk(iids, is_public=True, reason=''):
    """
    Atualiza uma lista de fascículos como público ou não público.

    - ``iids``: lista de iids de fascículos a serem atualizados, caso seja,
    lista vazia retorna um ValueError.
    - ``is_public``: boolean, filtra por público e não público.
    - ``reason``: string, indica o motivo pelo qual o issue é despublicado.
    """

    if not iids:
        raise ValueError(__(u'Obrigatório uma lista de ids.'))

    for issue in get_issues_by_iid(iids).values():
        issue.is_public = is_public
        issue.unpublish_reason = reason
        issue.save()


# -------- ARTICLE --------

def get_article_by_aid(aid, **kwargs):
    """
    Retorna um artigo considerando os parâmetros ``aid`` e ``kwargs``.

    - ``aid``: string, chave primaria do artigo (ex.: ``14a278af8d224fa2a09a901123ca78ba``);
    - ``kwargs``: parâmetros de filtragem.
    """

    if not aid:
        raise ValueError(__(u'Obrigatório um aid.'))

    return Article.objects(aid=aid, **kwargs).first()


def get_articles_by_aid(aids):
    """
    Retorna um dicionário de artigos aonde o atributo ``aid`` de cada um deles
    pertence a lista do parâmetro: ``aids``

    - ``aids``: lista de aids de artigos a serem filtrados.

    Em caso de não existir itens retorna {}.

    Exemplo do retorno:
        {
            u'aid12': <Article: article-aid12>,
            u'aid1': <Article: article-aid1>,
            u'aid123': <Article: article-aid123>
    """

    articles = Article.objects.in_bulk(aids)

    return articles


def set_article_is_public_bulk(aids, is_public=True, reason=''):
    """
    Atualiza uma lista de artigos como público ou não público.

    - ``aids``: lista de aids de artigos a serem atualizados, caso seja,
    lista vazia retorna um ValueError.
    - ``is_public``: boolean, filtra por público e não público.
    - ``reason``: string, indica o motivo pelo qual o artigo é despublicado.
    """

    if not aids:
        raise ValueError(__(u'Obrigatório uma lista de ids.'))

    for article in get_articles_by_aid(aids).values():
        article.is_public = is_public
        article.unpublish_reason = reason
        article.save()


def get_articles_by_iid(iid, **kwargs):
    """
    Retorna uma lista de artigos aonde o atributo ``iid`` de cada um deles
    é igual ao parâmetro: ``iid``.

    - ``iid``: chave primaria de fascículo para escolher os artigos.
    - ``kwargs``: parâmetros de filtragem.

    Em caso de não existir itens retorna {}.
    """

    if not iid:
        raise ValueError(__(u'Obrigatório uma lista de iid.'))

    return Article.objects(issue=iid, **kwargs)

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
