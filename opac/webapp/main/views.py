# coding: utf-8

import logging
from collections import OrderedDict
from flask_babelex import gettext as _
from flask import render_template, abort, current_app, request, session, redirect, jsonify, url_for

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


@main.before_request
def add_collection_to_g():
    if not hasattr(g, 'collection'):
        try:
            g.collection = controllers.get_current_collection()
        except Exception, e:
            # discutir o que fazer aqui
            g.collection = {}


@babel.localeselector
def get_locale():
    langs = current_app.config.get('LANGUAGES')
    lang_from_headers = request.accept_languages.best_match(langs.keys())

    if 'lang' not in session.keys():
        session['lang'] = lang_from_headers

    return session['lang']


@main.route('/set_locale/<string:lang_code>')
def set_locale(lang_code):
    langs = current_app.config.get('LANGUAGES')

    if lang_code not in langs.keys():
        abort(400, _(u'Código de idioma inválido'))

    # salvar o lang code na sessão
    session['lang'] = lang_code

    return redirect(request.referrer)


@main.route('/')
def index():
    return render_template("collection/index.html")


@main.route("/journals/search/alpha/ajax/", methods=['GET', ])
def journals_search_alpha_ajax():

    if not request.is_xhr:
        abort(400, _(u'Requisição inválida. Deve ser por ajax'))

    query = request.args.get('query', '', type=unicode)
    page = request.args.get('page', 1, type=int)
    response_data = controllers.get_alpha_list_from_paginated_journals(title_query=query, page=page)

    return jsonify(response_data)


@main.route("/journals/search/group/by/filter/ajax/", methods=['GET'])
def journals_search_by_theme_ajax():

    if not request.is_xhr:
        abort(400, _(u'Requisição inválida. Deve ser por ajax'))

    query = request.args.get('query', '', type=unicode)
    filter = request.args.get('filter', 'areas', type=unicode)

    if filter == 'areas':
        objects = controllers.get_journals_grouped_by('study_areas', query)
    elif filter == 'wos':
        objects = controllers.get_journals_grouped_by('index_at', query)
    elif filter == 'publisher':
        objects = controllers.get_journals_grouped_by('publisher_name', query)
    else:
        return jsonify({
            'error': 401,
            'message': u'Parámetro "filter" é inválido, deve ser "areas", "wos" ou "publisher".'
        })
    return jsonify(objects)


@main.route('/journals')
def collection_list_alpha():
    return render_template("collection/list_alpha.html")


@main.route('/journals/theme')
def collection_list_theme():
    return render_template("collection/list_theme.html")


@main.route('/journals/institution')
def collection_list_institution():
    return render_template("collection/list_institution.html")


@main.route('/journals/<string:journal_id>')
def journal_detail(journal_id):
    journal = controllers.get_journal_by_jid(journal_id)

    if not journal:
        abort(404, _(u'Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    # A ordenação padrão da função ``get_issues_by_jid``: "-year", "-volume", "order"
    issues = controllers.get_issues_by_jid(journal_id, is_public=True)

    # A lista de fascículos deve ter mais do que 1 item para que possamos tem
    # anterior e próximo
    if len(issues) >= 2:
        previous_issue = issues[1]
    else:
        previous_issue = None

    context = {
        'next_issue': None,
        'previous_issue': previous_issue,
        'journal': journal,
        # o primiero item da lista é o último fascículo.
        # condicional para verificar se issues contém itens
        'last_issue': issues[0] if issues else None
        }

    return render_template("journal/detail.html", **context)


@main.route('/journals/<string:journal_id>/issues')
def issue_grid(journal_id):
    journal = controllers.get_journal_by_jid(journal_id)

    if not journal:
        abort(404, _(u'Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    # A ordenação padrão da função ``get_issues_by_jid``: "-year", "-volume", "-order"
    issues = controllers.get_issues_by_jid(journal_id, is_public=True)

    result_dict = OrderedDict()
    for issue in issues:
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

    context = {
        'next_issue': None,
        'previous_issue': previous_issue,
        'journal': journal,
        'result_dict': result_dict,
        # o primiero item da lista é o último fascículo.
        # condicional para verificar se issues contém itens
        'last_issue': issues[0] if issues else None
    }
    return render_template("issue/grid.html", **context)


@main.route('/issues/<string:issue_id>')
def issue_toc(issue_id):
    issue = controllers.get_issue_by_iid(issue_id)

    if not issue:
        abort(404, _(u'Fascículo não encontrado'))

    if not issue.is_public:
        abort(404, ISSUE_UNPUBLISH + _(issue.unpublish_reason))

    if not issue.journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(issue.journal.unpublish_reason))

    journal = issue.journal
    articles = controllers.get_articles_by_iid(issue.iid, is_public=True)

    issues = controllers.get_issues_by_jid(journal.id, is_public=True)

    issue_list = [_issue for _issue in issues]

    previous_issue = utils.get_prev_issue(issue_list, issue)
    next_issue = utils.get_next_issue(issue_list, issue)

    result_dict = OrderedDict()
    for article in articles:
        section = article.get_section_by_lang(session.get('lang')[:2])
        result_dict.setdefault(section, [])
        result_dict[section].append(article)

    context = {
                'next_issue': next_issue,
                'previous_issue': previous_issue,
                'journal': journal,
                'issue': issue,
                'articles': result_dict,
                # o primiero item da lista é o último fascículo.
                'last_issue': issues[0] if issues else None
               }

    return render_template("issue/toc.html", **context)


@main.route('/articles/<string:article_id>')
def article_detail(article_id):
    article = controllers.get_article_by_aid(article_id)

    if not article:
        abort(404, _(u'Artigo não encontrado'))

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
        'issue': issue
    }

    return render_template("article/detail.html", **context)


@main.route('/articles/html/<string:article_id>')
def article_html_by_aid(article_id):
    article = controllers.get_article_by_aid(article_id)

    if not article:
        abort(404, _(u'Artigo não encontrado'))

    if not article.is_public:
        abort(404, ARTICLE_UNPUBLISH + _(article.unpublish_reason))

    if not article.htmls:
        abort(404, _(u'HTML do artigo não encontrado'))

    article_html = article.htmls[0].url

    return redirect(article_html)


@main.route('/abstract/<string:article_id>')
def abstract_detail(article_id):
    article = controllers.get_article_by_aid(article_id)

    if not article:
        abort(404, _(u'Resumo não encontrado'))

    if not article.is_public:
        abort(404, ARTICLE_UNPUBLISH + _(article.unpublish_reason))

    if not article.htmls:
        abort(404, _(u'Resumo do artigo não encontrado'))

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
        'issue': issue
    }
    return render_template("article/abstract.html", **context)


@main.route("/media/<path:filename>", methods=['GET'])
def download_file_by_filename(filename):
    media_root = current_app.config['MEDIA_ROOT']
    return send_from_directory(media_root, filename)


@main.route("/search", methods=['GET'])
def search():
    context = {}
    return render_template("collection/search.html", **context)


@main.route("/about", methods=['GET'])
def about():
    context = {}
    return render_template("collection/about.html", **context)


@main.route("/metrics", methods=['GET'])
def metrics():
    context = {}
    return render_template("collection/metrics.html", **context)
