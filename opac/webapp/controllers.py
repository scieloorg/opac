# coding: utf-8

"""
    Conjunto de funções utilitarias para acessar a camada de modelos,
    e agrupar esses resultados em estruturas de dados úties para as views
    ou outras camadas superiores, evitando assim que as camadas superiores
    acessem diretamente a camada inferior de modelos.
"""

import unicodecsv
import io
import xlsxwriter
import tweepy

from collections import OrderedDict

from slugify import slugify

from opac_schema.v1.models import (
    Journal,
    Issue,
    Article,
    Collection,
    News,
    Pages,
    PressRelease,
    Sponsor)
from flask import current_app, url_for
from flask_babelex import gettext as _
from flask_babelex import lazy_gettext as __
from flask_mongoengine import Pagination
from webapp import dbsql
from .models import User
from .choices import INDEX_NAME
from . import utils
from uuid import uuid4

from mongoengine import Q


# -------- COLLECTION --------

def get_current_collection():
    """
    Retorna o objeto coleção filtrando pela coleção cadastrada no arquivo de
    configuração ``OPAC_COLLECTION``.
    """
    current_collection_acronym = current_app.config['OPAC_COLLECTION']
    collection = Collection.objects.get(acronym=current_collection_acronym)
    return collection


def get_collection_tweets():
    tweets = []

    consumer_key = current_app.config['TWITTER_CONSUMER_KEY']
    consumer_secret = current_app.config['TWITTER_CONSUMER_SECRET']

    access_token = current_app.config['TWITTER_ACCESS_TOKEN']
    access_token_secret = current_app.config['TWITTER_ACCESS_TOKEN_SECRET']

    if all([consumer_key, consumer_secret, access_token, access_token_secret]):
        try:
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)

            api = tweepy.API(auth, timeout=2)
            public_tweets = api.user_timeline(count=10)
        except:
            return []
        else:
            tweets = [tweet for tweet in public_tweets]
        return tweets
    else:
        # falta pelo menos uma credencial do twitter
        return []


# -------- PRESSRELEASES --------

def get_press_release(journal, issue, lang_code, article=None):
    filters = {}

    if article:
        filters['article'] = article.id

    filters['journal'] = journal.id
    filters['issue'] = issue.id
    filters['language'] = lang_code

    return PressRelease.objects(**filters).first()


def get_press_releases(query_filter=None, order_by="publication_date"):
    if not query_filter:
        query_filter = {}

    return PressRelease.objects(**query_filter).order_by(order_by)


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
        raise ValueError("Parámetro: 'query_filter' é inválido!")
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
        "title": "Interface - Comunica\\u00e7\\u00e3o, Sa\\u00fade, Educa\\u00e7\\u00e3o"
    },
    """

    j_data = {
        'id': journal.id,
        'title': journal.title,
        'links': {
            'detail': url_for('main.journal_detail', url_seg=journal.url_segment),
            'submission': journal.online_submission_url or url_for('main.about_journal',
                                                                   url_seg=journal.url_segment) + '#submission',
            'instructions': url_for('main.about_journal', url_seg=journal.url_segment) + '#instructions',
            'about': url_for('main.about_journal', url_seg=journal.url_segment),
            'contact': url_for('main.about_journal', url_seg=journal.url_segment) + '#contact',
        },
        'is_active': journal.current_status == 'current',
        'issues_count': journal.issue_count,
    }

    if journal.last_issue:
        j_data['last_issue'] = {
            'volume': journal.last_issue.volume,
            'number': journal.last_issue.number,
            'year': journal.last_issue.year,
            'url_segment': journal.url_last_issue
        }

    return j_data


def get_alpha_list_from_paginated_journals(title_query, is_public=True, query_filter="", order_by="title_slug", page=1,
                                           per_page=20):
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
        que podem ser dados pelos campos: ``subject_categories``, ``study_areas``, ``index_at`` ou ``publisher_name``
        - para cada chave, se listam os periódicos nessa categoria, com a estrutura de dados
        retornada pela função: ``get_journal_json_data``
    """
    journals = get_journals(title_query, is_public, query_filter, order_by)

    groups_dict = {}

    for journal in journals:
        grouper_field_iterable = getattr(journal, grouper_field, None)
        if grouper_field_iterable:
            if isinstance(grouper_field_iterable, str):
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
        'themes_count': len(list(groups_dict.keys())),
    }

    return {'meta': meta, 'objects': groups_dict}


def get_journal_generator_for_csv(list_type='alpha', title_query='', is_public=True, order_by='title_slug',
                                  extension='xls'):
    def format_csv_row(list_type, journal):

        last_issue_volume = journal.last_issue.volume or ''
        last_issue_number = journal.last_issue.number or ''
        last_issue_year = journal.last_issue.year or ''

        common_fields = [
            str(journal.title),
            str(journal.issue_count),
            str(last_issue_volume) or '',
            str(last_issue_number) or '',
            str(last_issue_year) or '',
            str(journal.current_status == 'current'),
        ]

        if list_type == 'alpha':
            return common_fields
        elif list_type == 'areas':
            return [','.join(journal.study_areas)] + common_fields
        elif list_type == 'wos':
            return [','.join(journal.index_at)] + common_fields
        else:  # publisher_name
            return [journal.publisher_name] + common_fields

    common_headers = ['Title', 'issues', 'Last volume', 'Last number', 'Last year', 'Is active?']
    if list_type == 'alpha':
        csv_headers = common_headers
        order_by = 'title'
        worksheet_name = _('Lista Alfabética')
    elif list_type == 'areas':
        csv_headers = ['Areas', ] + common_headers
        order_by = 'study_areas'
        worksheet_name = _('Lista Temática')
    elif list_type == 'wos':
        csv_headers = ['WoS', ] + common_headers
        order_by = 'index_at'
        worksheet_name = _('Lista Web of Science')
    elif list_type == 'publisher':
        csv_headers = ['Publisher', ] + common_headers
        order_by = 'publisher_name'
        worksheet_name = _('Lista by Institution')

    journals = get_journals(title_query, is_public, order_by=order_by)

    if extension == 'csv':

        csv_file = io.StringIO()
        csv_writer = unicodecsv.writer(csv_file, encoding='utf-8')
        csv_writer.writerow(csv_headers)

        for journal in journals:
            csv_writer.writerow(format_csv_row(list_type, journal))
        csv_file.seek(0)

        return csv_file.getvalue()
    else:
        output = io.StringIO()

        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        worksheet = workbook.add_worksheet(worksheet_name)
        worksheet.set_column('A:A', 50)
        worksheet.set_column('C:C', 13)
        worksheet.set_column('D:D', 13)

        cell_head_format = workbook.add_format()
        cell_head_format.set_bg_color('#CCCCCC')
        cell_head_format.set_font_size(10)
        cell_head_format.set_bold()

        for i, head in enumerate(csv_headers):
            worksheet.write(0, i, head, cell_head_format)

        cell_format = workbook.add_format()
        cell_head_format.set_font_size(10)

        for i, journal in enumerate(journals):
            for j, data in enumerate(format_csv_row(list_type, journal)):
                # Adiciona 1 ao índice para maner o cabeçalho.
                worksheet.write(i + 1, j, data, cell_format)

        workbook.close()

        output.seek(0)

        return output.read()


def get_journal_by_jid(jid, **kwargs):
    """
    Retorna um periódico considerando os parâmetros ``jid`` e ``kwargs``

    - ``jid``: string, chave primaria do periódico (ex.: ``f8c87833e0594d41a89fe60455eaa5a5``);
    - ``kwargs``: parâmetros de filtragem.

    Em caso de não existir itens retorna {}.
    """

    if not jid:
        raise ValueError(__('Obrigatório um jid.'))

    return Journal.objects(jid=jid, **kwargs).first()


def get_journal_by_acron(acron, **kwargs):
    """
    Retorna um periódico considerando os parâmetros ``acron`` e ``kwargs``

    - ``acron``: string, acrônimo do periódico
    - ``kwargs``: parâmetros de filtragem.

    Em caso de não existir itens retorna {}.
    """

    if not acron:
        raise ValueError(__('Obrigatório um acronym.'))

    return Journal.objects(acronym=acron, **kwargs).first()


def get_journal_by_url_seg(url_seg, **kwargs):
    """
    Retorna um periódico considerando os parâmetros ``url_seg`` e ``kwargs``

    - ``url_seg``: string, acrônimo do periódico
    - ``kwargs``: parâmetros de filtragem.

    Em caso de não existir itens retorna {}.
    """

    if not url_seg:
        raise ValueError(__('Obrigatório um url_seg.'))

    return Journal.objects(url_segment=url_seg, **kwargs).first()


def get_journal_by_issn(issn, **kwargs):
    """
    Retorna um periódico considerando os parâmetros ``issn`` e ``kwargs``

    - ``issn``: string, issn do periódico
    - ``kwargs``: parâmetros de filtragem.

    Em caso de não existir itens retorna {}.
    """

    if not issn:
        raise ValueError(__('Obrigatório um issn.'))

    return Journal.objects(Q(print_issn=issn) | Q(eletronic_issn=issn), **kwargs).first()


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
        raise ValueError(__('Obrigatório uma lista de ids.'))

    for journal in list(get_journals_by_jid(jids).values()):
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
    issues_without_ahead = []

    if get_journal_by_jid(jid):
        issues = Issue.objects(
            journal=jid,
            type__in=['ahead', 'regular', 'special', 'supplement', 'volume_issue'],
            **kwargs).order_by(*order_by)
        issue_ahead = issues.filter(type='ahead').first()
        issues_without_ahead = issues.filter(type__ne='ahead')

    volume_issue = {}

    result_dict = OrderedDict()
    for issue in issues_without_ahead:

        key_year = str(issue.year)

        # Verificando se é um volume de fascículo e criando um dicionário auxiliar
        if issue.type == 'volume_issue':
            volume_issue.setdefault(issue.volume, {})
            volume_issue[issue.volume]['issue'] = issue
            volume_issue[issue.volume]['art_count'] = len(get_articles_by_iid(issue.iid))

        key_volume = issue.volume

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
        'ahead': issue_ahead,  # ahead of print
        'ordered_for_grid': result_dict,  # lista de fascículos odenadas para a grade
        'volume_issue': volume_issue,  # lista de volumes que são fascículos
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
        raise ValueError(__('Obrigatório um iid.'))

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
        raise ValueError(__('Obrigatório uma lista de ids.'))

    for issue in list(get_issues_by_iid(iids).values()):
        issue.is_public = is_public
        issue.unpublish_reason = reason
        issue.save()


def get_issue_by_acron_issue(jacron, year, issue_label):
    """
    Retorna um fascículo considerando os parâmetros ``iid`` e ``kwargs``.

    - ``jacron``: string, contendo o acrônimo do periódico;
    - ``issue``: string, label do issue.
    """

    jiid = get_journal_by_acron(jacron)

    if not jacron and year and issue_label:
        raise ValueError(__('Obrigatório um jacron e issue_label.'))

    return Issue.objects.filter(journal=jiid, year=int(year), label=issue_label).first()


def get_issue_by_pid(pid):
    """
    Retorna um fascículo considerando o parâmetro ``pid``.

    - ``pid``: string, contendo o PID do fascículo.
    """

    if not pid:
        raise ValueError(__('Obrigatório um PID.'))

    return Issue.objects.filter(pid=pid).first()


def get_issue_by_url_seg(url_seg, url_seg_issue):
    """
    Retorna um fascículo considerando os parâmetros ``iid`` e ``kwargs``.

    - ``url_seg``: string, contém o seguimento da URL do Journal;
    - ``url_seg_issue``: string, contém o seguimento da URL do Issue,.
    """

    jiid = get_journal_by_url_seg(url_seg)

    if not url_seg and url_seg_issue:
        raise ValueError(__('Obrigatório um url_seg e url_seg_issue.'))

    return Issue.objects.filter(journal=jiid, url_segment=url_seg_issue).first()


# -------- ARTICLE --------

def get_article_by_aid(aid, **kwargs):
    """
    Retorna um artigo considerando os parâmetros ``aid`` e ``kwargs``.

    - ``aid``: string, chave primaria do artigo (ex.: ``14a278af8d224fa2a09a901123ca78ba``);
    - ``kwargs``: parâmetros de filtragem.
    """

    if not aid:
        raise ValueError(__('Obrigatório um aid.'))

    return Article.objects(aid=aid, **kwargs).first()


def get_article_by_url_seg(url_seg_article, **kwargs):
    """
    Retorna um artigo considerando os parâmetros ``url_seg_article`` e ``kwargs``.

    - ``url_seg_article``: string, segmento do url do artigo;
    - ``kwargs``: parâmetros de filtragem.
    """

    if not url_seg_article:
        raise ValueError(__('Obrigatório um url_seg_article.'))

    return Article.objects(url_segment=url_seg_article, **kwargs).first()


def get_article_by_issue_article_seg(iid, url_seg_article, **kwargs):
    """
    Retorna um artigo considerando os parâmetros ``iid``, ``url_seg_article`` e
    ``kwargs``.

    - ``iid``: string, id do fascículo;
    - ``url_seg_article``: string, segmento do url do artigo;
    - ``kwargs``: parâmetros de filtragem.
    """

    if not iid and url_seg_article:
        raise ValueError(__('Obrigatório um iid and url_seg_article.'))

    return Article.objects(issue=iid, url_segment=url_seg_article, **kwargs).first()


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
        raise ValueError(__('Obrigatório uma lista de ids.'))

    for article in list(get_articles_by_aid(aids).values()):
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
        raise ValueError(__('Obrigatório um iid.'))

    return Article.objects(issue=iid, **kwargs).order_by('order')


def get_article_by_pid(pid, **kwargs):
    """
    Retorna um artigo considerando os parâmetros ``pid``.

    - ``pid``: string, contendo o PID do artigo.
    """

    if not pid:
        raise ValueError(__('Obrigatório um pid.'))

    return Article.objects(pid=pid, **kwargs).first()


# -------- NEWS --------


def create_news_record(news_model_data):
    try:
        news = News(**news_model_data)
        news._id = str(uuid4().hex)
        news.save()
    except Exception as e:
        raise e


def create_press_release_record(pr_model_data):
    try:
        pr = PressRelease.objects(**pr_model_data)[:1]

        if len(pr) == 0:  # On create add an id
            pr_model_data['_id'] = uuid4().hex

        pr.modify(upsert=True, new=True, **pr_model_data)

    except Exception as e:
        raise e


def get_latest_news_by_lang(language):
    limit = current_app.config['NEWS_LIST_LIMIT']
    return News.objects.filter(
        language=language,
        is_public=True).order_by('-publication_date')[:limit]


# -------- USER --------


def get_user_by_email(email):
    """
    Retorna o usuário aonde seu atributo ``email`` é igual ao parâmetro ``email``,
    caso não seja uma ``string`` retorna um ValueError.
    """

    if not isinstance(email, str):
        raise ValueError(__('Parâmetro email deve ser uma string'))

    return dbsql.session.query(User).filter_by(email=email).first()


def get_user_by_id(id):
    """
    Retorna o usuário aonde seu atributo ``id`` é igual ao parâmetro ``id``.
    """

    if not isinstance(id, int):
        raise ValueError(__('Parâmetro email deve ser uma inteiro'))

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
    elif type == 'news':
        return News.objects.count()
    elif type == 'sponsor':
        return Sponsor.objects.count()
    elif type == 'pressrelease':
        return PressRelease.objects.count()
    else:
        raise ValueError("Parâmetro 'type' errado, tente: 'journal' ou 'issue' ou 'article'.")


def send_email_share(from_email, recipents, share_url, subject, comment):
    """
    Envia uma mensagem de compartilhamento de página e retorna uma mensagem de
    confirmação
    @params:
    - ``from_email``: Email do usuário que compartilha a página
    - ``recipents`` : Liste de emials que compartilha a página
    - ``share_url`` : URL da página que compartilha
    - ``subject``   : Assunto
    - ``comment``   : Comentário adicional
    """
    subject = subject or __('Compartilhamento de link SciELO')
    share = __('O usuário %s compartilha este link: %s, da SciELO' % (from_email, share_url))
    comment = '%s<br/><br/>%s' % (share, comment)

    sent, message = utils.send_email(recipents, subject, comment)

    if not sent:
        return (sent, message)

    return (True, __('Mensagem enviada!'))


# -------- PAGES --------


def get_page_by_journal_acron_lang(acron, language):
    return Pages.objects(language=language, journal=acron).first()


def get_page_by_id(id):
    return Pages.objects.get(_id=id)


def get_pages_by_lang(lang, journal=''):
    return Pages.objects(language=lang, journal=journal)
