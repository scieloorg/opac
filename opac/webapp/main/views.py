# coding: utf-8
from __future__ import unicode_literals

import logging
from datetime import datetime
from collections import OrderedDict
from flask_babelex import gettext as _
from flask import render_template, abort, current_app, request, session, redirect, jsonify, url_for, Response
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin

from . import main
from flask import current_app, send_from_directory, g
from webapp import babel
from webapp import controllers
from webapp import models
from webapp import utils
import webapp

logger = logging.getLogger(__name__)

JOURNAL_UNPUBLISH = _(u"O periódico está indisponível por motivo de: ")
ISSUE_UNPUBLISH = _(u"O fascículo está indisponível por motivo de: ")
ARTICLE_UNPUBLISH = _(u"O artigo está indisponível por motivo de: ")


def url_external(endpoint, **kwargs):
    url = url_for(endpoint, **kwargs)
    return urljoin(request.url_root, url)


@main.before_app_request
def add_collection_to_g():
    if not hasattr(g, 'collection'):
        try:
            collection = controllers.get_current_collection()
            setattr(g, 'collection', collection)
        except Exception, e:
            # discutir o que fazer aqui
            setattr(g, 'collection', {})


@babel.localeselector
def get_locale():
    langs = current_app.config.get('LANGUAGES')
    lang_from_headers = request.accept_languages.best_match(langs.keys())

    if 'lang' not in session.keys():
        session['lang'] = lang_from_headers

    if not lang_from_headers and 'lang' not in session.keys():
        # Caso não seja possível detectar o idioma e não tenhamos a chave lang
        # no seção, fixamos o idioma padrão.
        session['lang'] = current_app.config.get('BABEL_DEFAULT_LOCALE')

    return session['lang']


@main.route('/set_locale/<string:lang_code>/')
def set_locale(lang_code):
    langs = current_app.config.get('LANGUAGES')

    if lang_code not in langs.keys():
        abort(400, _(u'Código de idioma inválido'))

    # salvar o lang code na sessão
    session['lang'] = lang_code

    return redirect(request.referrer)


@main.route('/')
def index():
    default_lang = current_app.config.get('BABEL_DEFAULT_LOCALE')
    language = session.get('lang', default_lang)

    news = controllers.get_latest_news_by_lang(language)
    analytics = controllers.get_collection_analytics()
    tweets = controllers.get_collection_tweets()
    press_releases = controllers.get_press_releases({'language': language})

    context = {
        'news': news,
        'analytics': analytics,
        'tweets': tweets,
        'press_releases': press_releases
    }

    return render_template("collection/index.html", **context)

###################################PressRelease#################################

@main.route('/<string:url_seg>/<regex("\d{4}\.(?:\w+)"):url_seg_issue>/pressrelease/<string:lang_code>/', defaults={'url_seg_article': None})
@main.route('/<string:url_seg>/<regex("\d{4}\.(?:\w+)"):url_seg_issue>/<string:url_seg_article>/pressrelease/<string:lang_code>/')
def pressrelease(url_seg, url_seg_issue, url_seg_article, lang_code):
    journal = controllers.get_journal_by_url_seg(url_seg)

    issue = controllers.get_issue_by_url_seg(journal.url_segment, url_seg_issue)

    if url_seg_article:
        article = controllers.get_article_by_url_seg(url_seg_article)
    else:
        article = None

    if not journal:
        abort(404, _(u'Periódico não encontrado'))

    if not issue:
        abort(404, _(u'Fascículo não encontrado'))

    press_release = controllers.get_press_release(journal, issue, lang_code, article)

    if not press_release:
        abort(404, _(u'Press Release não encontrado'))

    context = {
        'press_release': press_release
    }

    return render_template("includes/press_release.html", **context)


###################################Collection###################################

@main.route('/journals/')
def collection_list():
    return render_template("collection/list_journal.html")


@main.route('/journals/feed/')
def collection_list_feed():
    default_lang = current_app.config.get('BABEL_DEFAULT_LOCALE')
    language = session.get('lang', default_lang) or default_lang
    collection = controllers.get_current_collection()

    title = 'SciELO - %s - %s' % (collection.name, _(u'Últimos periódicos inseridos na coleção'))
    subtitle = _(u'10 últimos periódicos inseridos na coleção %s' % collection.name)

    feed = AtomFeed(title,
                    subtitle=subtitle,
                    logo=utils.get_resources_url(g.collection.logo_resource,
                                                 'img', language),
                    feed_url=request.url, url=request.url_root)

    journals = controllers.get_journals_paginated(
        title_query='', page=1, order_by='-created', per_page=10)

    if not journals.items:
        feed.add(u'Nenhum periódico encontrado',
                 url=request.url,
                 updated=datetime.now())

    for journal in journals.items:
        issues = controllers.get_issues_by_jid(journal.jid, is_public=True)
        last_issue = issues[0] if issues else None

        articles = []
        if last_issue:
            articles = controllers.get_articles_by_iid(last_issue.iid,
                                                       is_public=True)

        result_dict = OrderedDict()
        for article in articles:
            section = article.get_section_by_lang(language[:2])
            result_dict.setdefault(section, [])
            result_dict[section].append(article)

        context = {
            'journal': journal,
            'articles': result_dict,
            'language': language,
            'last_issue': last_issue
        }

        feed.add(journal.title,
                 render_template("collection/list_feed_content.html", **context),
                 content_type='html',
                 author=journal.publisher_name,
                 url=url_external('main.journal_detail', url_seg=journal.url_segment),
                 updated=journal.updated,
                 published=journal.created)

    return feed.get_response()


@main.route("/collection/about/", methods=['GET'])
def about_collection():
    default_lang = current_app.config.get('BABEL_DEFAULT_LOCALE')
    language = session.get('lang', default_lang) or default_lang

    context = {}

    for page in getattr(g.collection, 'about', []):
        if page.language == language:
            context = {'content': page.content}

    return render_template("collection/about.html", **context)

####################################Journal#####################################

@main.route('/<string:url_seg>/')
def journal_detail(url_seg):
    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _(u'Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    # todo: ajustar para que seja só noticias relacionadas ao periódico
    default_lang = current_app.config.get('BABEL_DEFAULT_LOCALE')
    language = session.get('lang', default_lang)
    news = controllers.get_latest_news_by_lang(language)

    # A ordenação padrão da função ``get_issues_by_jid``: "-year", "-volume", "order"
    issues = controllers.get_issues_by_jid(journal.id, is_public=True)

    # A lista de fascículos deve ter mais do que 1 item para que possamos tem
    # anterior e próximo
    if len(issues) >= 2:
        previous_issue = issues[1]
    else:
        previous_issue = None

    # Get press releases
    press_releases = controllers.get_press_releases({'journal': journal,
                                                     'language': language})

    context = {
        'next_issue': None,
        'previous_issue': previous_issue,
        'journal': journal,
        'press_releases': press_releases,
        # o primiero item da lista é o último fascículo.
        # condicional para verificar se issues contém itens
        'last_issue': issues[0] if issues else None,
        'news': news
    }

    return render_template("journal/detail.html", **context)


@main.route('/<string:url_seg>/feed/')
def journal_feed(url_seg):
    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _(u'Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    issues = controllers.get_issues_by_jid(journal.jid, is_public=True)
    last_issue = issues[0] if issues else None
    articles = controllers.get_articles_by_iid(last_issue.iid, is_public=True)

    feed = AtomFeed(journal.title,
                    feed_url=request.url,
                    url=request.url_root,
                    subtitle=utils.get_label_issue(last_issue))

    # ######### TODO: Revisar/Melhorar/Consertar #########
    try:
        feed_language = session['lang'][:2].lower()
    except Exception, e:
        feed_language = 'pt'

    for article in articles:

        # ######### TODO: Revisar #########
        article_lang = feed_language
        if feed_language not in article.languages:
            article_lang = article.original_language

        feed.add(article.title or 'NO TITLE',
                 render_template("issue/feed_content.html", article=article),
                 content_type='html',
                 author=article.authors,
                 url=url_external('main.article_detail',
                                  url_seg=journal.url_segment,
                                  url_seg_issue=last_issue.url_segment,
                                  url_seg_article=article.url_segment,
                                  lang_code=article_lang),
                 updated=journal.updated,
                 published=journal.created)

    return feed.get_response()


@main.route("/<string:url_seg>/about/", methods=['GET'])
def about_journal(url_seg):
    default_lang = current_app.config.get('BABEL_DEFAULT_LOCALE')
    language = session.get('lang', default_lang) or default_lang

    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _(u'Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    # A ordenação padrão da função ``get_issues_by_jid``: "-year", "-volume", "order"
    issues = controllers.get_issues_by_jid(journal.id, is_public=True)

    # A lista de fascículos deve ter mais do que 1 item para que possamos tem
    # anterior e próximo
    if len(issues) >= 2:
        previous_issue = issues[1]
    else:
        previous_issue = None

    page = controllers.get_page_by_journal_acron_lang(journal.acronym, language)

    context = {
        'next_issue': None,
        'previous_issue': previous_issue,
        'journal': journal,
        # o primiero item da lista é o último fascículo.
        # condicional para verificar se issues contém itens
        'last_issue': issues[0] if issues else None,
    }

    if page:
        context['content'] = page.content

    return render_template("journal/about.html", **context)


@main.route("/journals/search/alpha/ajax/", methods=['GET', ])
def journals_search_alpha_ajax():

    if not request.is_xhr:
        abort(400, _(u'Requisição inválida. Deve ser por ajax'))

    query = request.args.get('query', '', type=unicode)
    query_filter = request.args.get('query_filter', '', type=unicode)
    page = request.args.get('page', 1, type=int)
    response_data = controllers.get_alpha_list_from_paginated_journals(
        title_query=query, query_filter=query_filter, page=page)

    return jsonify(response_data)


@main.route("/journals/search/group/by/filter/ajax/", methods=['GET'])
def journals_search_by_theme_ajax():

    if not request.is_xhr:
        abort(400, _(u'Requisição inválida. Deve ser por ajax'))

    query = request.args.get('query', '', type=unicode)
    query_filter = request.args.get('query_filter', '', type=unicode)
    filter = request.args.get('filter', 'areas', type=unicode)

    if filter == 'areas':
        objects = controllers.get_journals_grouped_by('study_areas', query, query_filter=query_filter)
    elif filter == 'wos':
        objects = controllers.get_journals_grouped_by('index_at', query, query_filter=query_filter)
    elif filter == 'publisher':
        objects = controllers.get_journals_grouped_by('publisher_name', query, query_filter=query_filter)
    else:
        return jsonify({
            'error': 401,
            'message': _(u'Parámetro "filter" é inválido, deve ser "areas", "wos" ou "publisher".')
        })
    return jsonify(objects)


@main.route("/journals/download/<string:list_type>/<string:extension>/", methods=['GET', ])
def download_journal_list(list_type, extension):
    if extension.lower() not in ['csv', 'xls']:
        abort(401, _(u'Parámetro "extension" é inválido, deve ser "csv" ou "xls".'))
    elif list_type.lower() not in ['alpha', 'areas', 'wos', 'publisher']:
        abort(401, _(u'Parámetro "list_type" é inválido, deve ser: "alpha", "areas", "wos" ou "publisher".'))
    else:
        if extension.lower() == 'xls':
            mimetype = 'application/vnd.ms-excel'
        else:
            mimetype = 'text/csv'
        query = request.args.get('query', '', type=unicode)
        data = controllers.get_journal_generator_for_csv(list_type=list_type, title_query=query)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = 'journals_%s_%s.%s' % (list_type, timestamp, extension)
        response = Response(data, mimetype=mimetype)
        response.headers['Content-Disposition'] = u'attachment; filename=%s' % filename
        return response

####################################Issue#######################################

@main.route('/<string:url_seg>/issues/')
def issue_grid(url_seg):
    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _(u'Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    # A ordenação padrão da função ``get_issues_by_jid``: "-year", "-volume", "-order"
    issues_data = controllers.get_issues_for_grid_by_jid(journal.id, is_public=True)

    context = {
        'journal': journal,
        'next_issue': None,
        'previous_issue': issues_data['previous_issue'],
        'last_issue': issues_data['last_issue'],
        'volume_issue': issues_data['volume_issue'],
        'ahead': issues_data['ahead'],
        'result_dict': issues_data['ordered_for_grid'],
    }
    return render_template("issue/grid.html", **context)


@main.route('/<string:url_seg>/<regex("\d{4}\.(?:\w+)"):url_seg_issue>/')
def issue_toc(url_seg, url_seg_issue):
    default_lang = current_app.config.get('BABEL_DEFAULT_LOCALE')
    section_filter = request.args.get('section', '', type=unicode)

    if not session.get('lang'):
        lang = default_lang
    else:
        lang = session.get('lang')[:2]

    issue = controllers.get_issue_by_url_seg(url_seg, url_seg_issue)

    if not issue:
        abort(404, _(u'Fascículo não encontrado'))

    if not issue.is_public:
        abort(404, ISSUE_UNPUBLISH + _(issue.unpublish_reason))

    if not issue.journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(issue.journal.unpublish_reason))

    journal = issue.journal
    articles = controllers.get_articles_by_iid(issue.iid, is_public=True)

    if articles:
        sections = sorted(articles.item_frequencies('section').keys())
    else:
        sections = []

    issues = controllers.get_issues_by_jid(journal.id, is_public=True)

    if section_filter != u'':
        articles = articles.filter(section__iexact=section_filter)

    issue_list = [_issue for _issue in issues]

    previous_issue = utils.get_prev_issue(issue_list, issue)
    next_issue = utils.get_next_issue(issue_list, issue)

    context = {
                'next_issue': next_issue,
                'previous_issue': previous_issue,
                'journal': journal,
                'issue': issue,
                'articles': articles,
                'sections': sections,
                'section_filter': section_filter,
                # o primiero item da lista é o último fascículo.
                'last_issue': issues[0] if issues else None
               }

    return render_template("issue/toc.html", **context)


@main.route('/<string:url_seg>/<regex("\d{4}\.(?:\w+)"):url_seg_issue>/feed/')
def issue_feed(url_seg, url_seg_issue):
    issue = controllers.get_issue_by_url_seg(url_seg, url_seg_issue)

    if not issue:
        abort(404, _(u'Fascículo não encontrado'))

    if not issue.is_public:
        abort(404, ISSUE_UNPUBLISH + _(issue.unpublish_reason))

    if not issue.journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(issue.journal.unpublish_reason))

    journal = issue.journal
    articles = controllers.get_articles_by_iid(issue.iid, is_public=True)

    feed = AtomFeed(journal.title or "",
                    feed_url=request.url,
                    url=request.url_root,
                    subtitle=utils.get_label_issue(issue))

    # ######### TODO: Revisar/Melhorar/Consertar #########
    try:
        feed_language = session['lang'][:2].lower()
    except Exception, e:
        feed_language = 'pt'

    for article in articles:
        # ######### TODO: Revisar #########
        article_lang = feed_language
        if feed_language not in article.languages:
            article_lang = article.original_language

        feed.add(article.title or 'Unknow title',
                 render_template("issue/feed_content.html", article=article),
                 content_type='html',
                 author=article.authors,
                 url=url_external('main.article_detail',
                                  url_seg=journal.url_segment,
                                  url_seg_issue=issue.url_segment,
                                  url_seg_article=article.url_segment,
                                  lang_code=article_lang),
                 updated=journal.updated,
                 published=journal.created)

    return feed.get_response()

###################################Article######################################

@main.route('/<string:url_seg>/<regex("\d{4}\.(?:\w+)"):url_seg_issue>/<string:url_seg_article>/')
@main.route('/<string:url_seg>/<regex("\d{4}\.(?:\w+)"):url_seg_issue>/<string:url_seg_article>/<regex("(?:\w{2})"):lang_code>/')
def article_detail(url_seg, url_seg_issue, url_seg_article, lang_code=''):

    issue = controllers.get_issue_by_url_seg(url_seg, url_seg_issue)

    if not issue:
        abort(404, _(u'Issue não encontrado'))

    article = controllers.get_article_by_issue_article_seg(issue.iid, url_seg_article)

    if not article:
        abort(404, _(u'Artigo não encontrado'))

    if lang_code not in article.languages:
        # Se não tem idioma na URL mostra o artigo no idioma original.
        lang_code = article.original_language

    if not article.is_public:
        abort(404, ARTICLE_UNPUBLISH + _(article.unpublish_reason))

    if not article.issue.is_public:
        abort(404, ISSUE_UNPUBLISH + _(article.issue.unpublish_reason))

    if not article.journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(article.journal.unpublish_reason))

    journal = article.journal
    issue = article.issue

    articles = controllers.get_articles_by_iid(issue.iid, is_public=True)

    article_list = [_article for _article in articles]

    previous_article = utils.get_prev_article(article_list, article)
    next_article = utils.get_next_article(article_list, article)

    context = {
        'next_article': next_article,
        'previous_article': previous_article,
        'article': article,
        'journal': journal,
        'issue': issue,
        'article_lang': lang_code
    }

    return render_template("article/detail.html", **context)


###################################Search#######################################

@main.route("/metasearch/", methods=['GET'])
def metasearch():
    url = request.args.get('url', current_app.config['URL_SEARCH'], type=unicode)
    params = {}
    for k, v in request.args.items():
        if k != 'url':
            params[k] = v
    xml = utils.do_request(url, request.args)
    return Response(xml, mimetype='text/xml')

###################################Others#######################################

@main.route("/media/<path:filename>/", methods=['GET'])
def download_file_by_filename(filename):
    media_root = current_app.config['MEDIA_ROOT']
    return send_from_directory(media_root, filename)


@main.route("/open_access/", methods=['GET'])
def open_access():
    return render_template("open_access.html")
