# coding: utf-8

"""
    Conjunto de funções utilitarias para acessar a camada de modelos,
    e agrupar esses resultados em estruturas de dados úties para as views
    ou outras camadas superiores, evitando assim que as camadas superiores
    acessem diretamente a camada inferior de modelos.
"""

import datetime
import unicodecsv
import cStringIO
from collections import OrderedDict

from slugify import slugify

from opac_schema.v1.models import Journal, Issue, Article, Collection, News, Pages
from flask import current_app, url_for
from flask_babelex import lazy_gettext as __
from flask_mongoengine import Pagination
from flask_oauthlib.client import OAuth
from webapp import dbsql
from models import User
from choices import INDEX_NAME
import utils


ANALYTICS = 'http://analytics.scielo.org'

# -------- COLLECTION --------

def get_current_collection():
    """
    Retorna o objeto coleção filtrando pela coleção cadastrada no arquivo de
    configuração ``OPAC_COLLECTION``.
    """
    current_collection_acronym = current_app.config['OPAC_COLLECTION']
    collection = Collection.objects.get(acronym=current_collection_acronym)
    return collection


def get_collection_analytics():
    """
    Regresa una colección con las metricas y urls de SciELO Analytics
    """
    current_collection_acronym = current_app.config['OPAC_COLLECTION']
    endpoint = 'ajx/publication/size'
    params = {
        'code': current_collection_acronym,
        'collection': current_collection_acronym,
        'field': 'citations'
    }
    references = utils.do_request_json('{0}/{1}'.format(ANALYTICS, endpoint), params)

    params['field'] = 'documents'
    articles = utils.do_request_json('{0}/{1}'.format(ANALYTICS, endpoint), params)

    params['field'] = 'issue'
    issues = utils.do_request_json('{0}/{1}'.format(ANALYTICS, endpoint), params)

    params['field'] = 'issn'
    journals = utils.do_request_json('{0}/{1}'.format(ANALYTICS, endpoint), params)

    analytics = {}
    analytics['metrics'] = {
        'references': int(references.get('total', 0)),
        'articles': int(articles.get('total', 0)),
        'issues': int(issues.get('total', 0)),
        'journals': int(journals.get('total', 0)),
    }
    analytics['urls'] = {
        'downloads': '{0}/w/accesses?collection={1}'.format(ANALYTICS, current_collection_acronym),
        'references': '{0}/w/publication/size?collection={1}'.format(ANALYTICS, current_collection_acronym),
        'other': '{0}/?collection={1}'.format(ANALYTICS, current_collection_acronym),
    }

    return analytics


def get_collection_tweets():

    tweets = []
    oauth = OAuth(current_app)
    twitter = oauth.remote_app(
        'twitter',
        base_url='https://api.twitter.com/1.1/',
        request_token_url='https://api.twitter.com/oauth/request_token',
        access_token_url='https://api.twitter.com/oauth/access_token',
        authorize_url='https://api.twitter.com/oauth/authenticate',
        consumer_key=current_app.config['TWITTER_CONSUMER_KEY'],
        consumer_secret=current_app.config['TWITTER_CONSUMER_SECRET']
    )

    @twitter.tokengetter
    def get_twitter_token():
        return (
            current_app.config['TWITTER_ACCESS_TOKEN'],
            current_app.config['TWITTER_ACCESS_TOKEN_SECRET']
        )

    response = twitter.request('statuses/user_timeline.json', data={
        'screen_name': current_app.config['TWITTER_SCREEN_NAME'],
        'count': current_app.config['TWITTER_LIMIT'],
    })

    if response.status == 200:
        tweets = response.data

    return tweets


# -------- JOURNAL --------

def get_journals(title_query='', is_public=True, query_filter="", order_by="title_slug"):
    """
    Retorna uma lista de periódicos considerando os parâmetros:
    - ``title_query`` texto para filtrar (usando i_contains) pelo titulo do periódicos;
    - ``is_public``: filtra por público e não público de cada periódico;
    - ``query_filter``: string com possíveis valores:
        - "" (vazio == sem filtro)
        - "current" (somente periódicos ativos)
        - "no-current" (somente periódicos não ativos)
    - ``order_by``: que corresponde ao nome de um atributo pelo qual
                    deve estar ordenada a lista resultante.
    """
    filters = {}

    if query_filter not in ["", "current", "no-current"]:
        raise ValueError(u"Parámetro: 'query_filter' é inválido!")
    elif query_filter == "current":
        filters = {
            "current_status": "current",
        }
    elif query_filter == "no-current":
        filters = {
            "current_status__ne": "current",
        }

    if not title_query or title_query.strip() == "":
        journals = Journal.objects(
            is_public=is_public, **filters).order_by(order_by)
    else:
        title_query_slug = slugify(title_query)
        journals = Journal.objects(
            is_public=is_public,
            title_slug__icontains=title_query_slug,
            **filters).order_by(order_by)

    return journals


def get_journals_paginated(title_query, is_public=True, query_filter="", order_by="title_slug", page=1, per_page=20):
    """
    Retorna um objeto Pagination (flask-mongoengine) com a lista de periódicos filtrados
    pelo titulo (title_query) e pelo parametro ``is_public``, ordenado pelo campo indicado
    pelo parametro ``order_by``.
    Os parametros:
    - ``page`` indica o número da pagina;
    - ``per_page`` indica o tamanho da pagina.
    """

    journals = get_journals(title_query, is_public, query_filter, order_by)
    return Pagination(journals, page, per_page)


def get_journal_json_data(journal):
    """
    Para cada journal, retorna uma estrutura mais resumida para ser enviada como json
    para o frontend.

    Exemplo:

    {
        "id": "e3ad10cca39a466da771c8abe6591a9f",
        "is_active": true,
        "issues_count": 64,
        "last_issue": {
            "number": "123",
            "volume": 456,
            "year": 2016
        },
        "links": {
            "about": "#",
            "contact": "#",
            "detail": "/journals/e3ad10cca39a466da771c8abe6591a9f",
            "instructions": "#",
            "submission": "#"
        },
        "title": "Interface - Comunica\u00e7\u00e3o, Sa\u00fade, Educa\u00e7\u00e3o"
    },
    """

    j_data = {
        'id': journal.id,
        'title': journal.title,
        'links': {
            'detail': url_for('main.journal_detail', journal_id=journal.jid),
            'submission': '#',
            'instructions': '#',
            'about': '#',
            'contact': '#',
        },
        'is_active': journal.current_status == 'current',
        'issues_count': journal.issue_count,
    }

    if journal.last_issue:
        j_data['last_issue'] = {
            'volume': journal.last_issue.volume,
            'number': journal.last_issue.number,
            'year': journal.last_issue.year,
        }

    return j_data


def get_alpha_list_from_paginated_journals(title_query, is_public=True, query_filter="", order_by="title_slug", page=1, per_page=20):
    """
    Retorna a estrutura de dados com a lista alfabética de periódicas, e da paginação para montar a listagem alfabética.
    """

    journals = get_journals_paginated(
        title_query=title_query, query_filter=query_filter,
        order_by=order_by, page=page, per_page=per_page)
    journal_list = []

    for journal in journals.items:
        j_data = get_journal_json_data(journal)
        journal_list.append(j_data)

    response_data = {
        'current_page': page,
        'total_pages': journals.pages,
        'total': journals.total,
        'has_prev': journals.has_prev,
        'prev_num': journals.prev_num,
        'has_next': journals.has_next,
        'next_num': journals.next_num,
        'journals': journal_list
    }
    return response_data


def get_journals_grouped_by(grouper_field, title_query='', query_filter='', is_public=True, order_by="title_slug"):
    """
    Retorna dicionário com 2 chaves: ``meta`` e ``objects``.

    - ``meta`` é um dicionario de metadados, que contém:
        - ``total`` com a quantidade total de periódicos retornados;
        - ``themes_count`` com a quantidade de chaves dentro do dict ``objects``
    - ``objects`` é um dicionario de periódicos agrupados pela área de conhecimento.
        - cada chave é definida pelos valores do campo indicado pelo param: ``grouper_field``
        que podem ser dados pelos campos: ``study_areas``, ``index_at``, ou ``publisher_name``
        - para cada chave, se listam os periódicos nessa categoria, com a estrutura de dados
        retornada pela função: ``get_journal_json_data``
    """
    journals = get_journals(title_query, is_public, query_filter, order_by)

    groups_dict = {}

    for journal in journals:
        grouper_field_iterable = getattr(journal, grouper_field, None)
        if grouper_field_iterable:
            if isinstance(grouper_field_iterable, unicode):
                grouper_field_iterable = [grouper_field_iterable]
        else:
            continue

        for grouper in grouper_field_iterable:

            if grouper_field == 'index_at':
                # tentavida de pegar o nome e não a sigla do index
                # se não achar o nome (KeyError), ficamos com o nome da sigla
                grouper = INDEX_NAME.get(grouper, grouper)

            j_data = get_journal_json_data(journal)
            groups_dict.setdefault(grouper, []).append(j_data)

    meta = {
        'total': journals.count(),
        'themes_count': len(groups_dict.keys()),
    }

    return {'meta': meta, 'objects': groups_dict}


def get_journal_generator_for_csv(list_type='alpha', title_query='', is_public=True, order_by='title_slug'):

    def format_csv_row(list_type, journal):
        common_fields = [
            unicode(journal.title),
            unicode(journal.issue_count),
            unicode(journal.last_issue.volume) or u'',
            unicode(journal.last_issue.number) or u'',
            unicode(journal.last_issue.year) or u'',
            unicode(journal.current_status == 'current'),
        ]
        if list_type == 'alpha':
            return common_fields
        elif list_type == 'areas':
            return [','.join(journal.study_areas)] + common_fields
        elif list_type == 'wos':
            return [','.join(journal.index_at)] + common_fields
        else:  # publisher_name
            return [journal.publisher_name] + common_fields

    common_headers = ['Title', '# issues', 'Last volume', 'Last number', 'Last year', 'Is active?']
    if list_type == 'alpha':
        CSV_HEADERS = common_headers
        order_by = 'title'
    elif list_type == 'areas':
        CSV_HEADERS = ['areas', ] + common_headers
        order_by = 'study_areas'
    elif list_type == 'wos':
        CSV_HEADERS = ['WoS', ] + common_headers
        order_by = 'index_at'
    elif list_type == 'publisher':
        CSV_HEADERS = ['Publisher', ] + common_headers
        order_by = 'publisher_name'

    csv_file = cStringIO.StringIO()
    csv_writer = unicodecsv.writer(csv_file, encoding='utf-8')
    csv_writer.writerow(CSV_HEADERS)

    journals = get_journals(title_query, is_public, order_by=order_by)

    for journal in journals:
        csv_writer.writerow(format_csv_row(list_type, journal))
    csv_file.seek(0)
    return csv_file.getvalue()


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


def get_journal_by_acron(acron, **kwargs):
    """
    Retorna um periódico considerando os parâmetros ``acron`` e ``kwargs``

    - ``acron``: string, acrônimo do periódico
    - ``kwargs``: parâmetros de filtragem.

    Em caso de não existir itens retorna {}.
    """

    if not acron:
        raise ValueError(__(u'Obrigatório um acronym.'))

    return Journal.objects(acronym=acron, **kwargs).first()


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
        order_by = ["-year", "-volume", "-order"]

    if get_journal_by_jid(jid):
        return Issue.objects(journal=jid, **kwargs).order_by(*order_by)


def get_issues_for_grid_by_jid(jid, **kwargs):
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
        order_by = ["-year", "-volume", "-order"]

    issues = []
    issues_ahead = []
    issues_without_ahead = []

    if get_journal_by_jid(jid):
        issues = Issue.objects(
            journal=jid,
            type__in=['ahead', 'regular', 'special', 'supplement'],
            **kwargs).order_by(*order_by)
        issues_ahead = issues.filter(type='ahead')
        issues_without_ahead = issues.filter(type__ne='ahead')

    result_dict = OrderedDict()
    for issue in issues_without_ahead:
        key_year = str(issue.year)
        key_volume = str(issue.volume)
        result_dict.setdefault(key_year, OrderedDict())
        result_dict[key_year].setdefault(key_volume, []).append(issue)

    # A lista de fascículos deve ter mais do que 1 item para que possamos tem
    # anterior e próximo
    if len(issues) >= 2:
        previous_issue = issues[1]
    else:
        previous_issue = None

    # o primiero item da lista é o último fascículo.
    # condicional para verificar se issues contém itens
    last_issue = issues[0] if issues else None

    return {
        'only_ahead': issues_ahead,         # lista de fascículos ahead of print
        'ordered_for_grid': result_dict,    # lista de fascículos odenadas para a grade
        'previous_issue': previous_issue,
        'last_issue': last_issue
    }


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
    é igual ao parâmetro: ``iid`` ordenado pelo atributo order.

    - ``iid``: chave primaria de fascículo para escolher os artigos.
    - ``kwargs``: parâmetros de filtragem.

    Em caso de não existir itens retorna {}.

    """

    if not iid:
        raise ValueError(__(u'Obrigatório um iid.'))

    return Article.objects(issue=iid, **kwargs).order_by('order')

# -------- NEWS --------


def create_news_record(news_model_data):
    try:
        from uuid import uuid4
        news = News(**news_model_data)
        news._id = unicode(uuid4().hex)
        news.save()
    except Exception, e:
        raise e


def get_latest_news_by_lang(language):
    limit = current_app.config['NEWS_LIST_LIMIT']
    return News.objects.filter(
        language=language,
        is_public=True).order_by('-publication_date')[:limit]


def get_page_by_journal_acron_lang(acron, language):

    page = Pages.objects(language=language, journal=acron).first()

    return page

# -------- SLQALCHEMY --------


# -------- USER --------


def get_user_by_email(email):
    """
    Retorna o usuário aonde seu atributo ``email`` é igual ao parâmetro ``email``,
    caso não seja uma ``string`` retorna um ValueError.
    """

    if not isinstance(email, basestring):
        raise ValueError(__(u'Parâmetro email deve ser uma string'))

    return dbsql.session.query(User).filter_by(email=email).first()


def get_user_by_id(id):
    """
    Retorna o usuário aonde seu atributo ``id`` é igual ao parâmetro ``id``.
    """

    if not isinstance(id, int):
        raise ValueError(__(u'Parâmetro email deve ser uma inteiro'))

    return dbsql.session.query(User).get(id)


def set_user_email_confirmed(user):
    """
    Atualiza o usuário ``user`` deixando ele com email confirmado
    (atributo ``email_confirmed`` = True).
    """

    if not isinstance(user, User):
        raise ValueError(__('Usuário deve ser do tipo %s' % User))

    user.email_confirmed = True
    dbsql.session.add(user)
    dbsql.session.commit()


def set_user_password(user, password):
    """
    Atualiza o usuário ``user`` com a senha definida pelo parâmetro
    ``password``.
    """

    if not isinstance(user, User):
        raise ValueError(__('Usuário deve ser do tipo %s' % User))

    user.password = password
    dbsql.session.add(user)
    dbsql.session.commit()


# -------- FUNCTIONS --------


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
