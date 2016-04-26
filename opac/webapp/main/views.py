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


@main.route("/journals/search/ajax/", methods=['GET', 'POST'])
def journals_search_ajax():
    per_page = 20
    query = request.args.get('query', '', type=str)
    page = request.args.get('page', 1, type=int)
    journals = controllers.get_journals_paginated(
        title_query=query,
        page=page,
        per_page=per_page,
    )
    current_page = page
    total_pages = journals.pages
    total = journals.total
    journal_list = []
    for journal in journals.items:
        j_data = {
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
            'last_issue': {
                'volume': journal.last_issue.volume,
                'number': journal.last_issue.number,
                'year': journal.last_issue.year,
            }
        }
        journal_list.append(j_data)

    response_data = {
        'current_page': current_page,
        'total_pages': total_pages,
        'total': total,
        'has_prev': journals.has_prev,
        'prev_num': journals.prev_num,
        'has_next': journals.has_next,
        'next_num': journals.next_num,
        'journals': journal_list
    }

    return jsonify(response_data)


@main.route('/journals')
def collection_list_alpha():
    context = {}
    return render_template("collection/list_alpha.html", **context)


@main.route('/journals/theme')
def collection_list_theme():
    objects_by_area = controllers.get_journals_by_study_area()
    objects_by_indexer = controllers.get_journals_by_indexer()

    context = {
        'objects_by_area': objects_by_area,
        'objects_by_indexer': objects_by_indexer
    }

    return render_template("collection/list_theme.html", **context)


@main.route('/journals/institution')
def collection_list_institution():
    context = controllers.get_journals_by_sponsor()

    return render_template("collection/list_institution.html", **context)


@main.route('/journals/<string:journal_id>')
def journal_detail(journal_id):
    journal = controllers.get_journal_by_jid(journal_id)

    if not journal:
        abort(404, _(u'Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    context = {'journal': journal}

    return render_template("journal/detail.html", **context)


@main.route('/journals/<string:journal_id>/issues')
def issue_grid(journal_id):
    journal = controllers.get_journal_by_jid(journal_id)

    if not journal:
        abort(404, _(u'Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    issues = controllers.get_issues_by_jid(journal_id, is_public=True)

    result_dict = OrderedDict()
    for issue in issues:
        key_year = str(issue.year)
        key_volume = str(issue.volume)
        result_dict.setdefault(key_year, OrderedDict())
        result_dict[key_year].setdefault(key_volume, []).append(issue)

    context = {
        'journal': journal,
        'result_dict': result_dict,
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
    articles = controllers.get_articles_by_iid(issue.iid)

    context = {'journal': journal,
               'issue': issue,
               'articles': articles}

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

    context = {
        'article': article,
        'journal': article.journal,
        'issue': article.issue
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

    return article_html


@main.route('/abstract/<string:article_id>')
def abstract_detail(article_id):
    article = controllers.get_article_by_aid(article_id)

    if not article:
        abort(404, _(u'Resumo não encontrado'))

    if not article.is_public:
        abort(404, ARTICLE_UNPUBLISH + _(article.unpublish_reason))

    if not article.htmls:
        abort(404, _(u'Resumo do artigo não encontrado'))

    context = {
        'article': article,
        'journal': article.journal,
        'issue': article.issue
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
