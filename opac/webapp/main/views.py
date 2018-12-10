# coding: utf-8

import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from collections import OrderedDict
from flask_babelex import gettext as _
from flask import render_template, abort, current_app, request, session, redirect, jsonify, url_for, Response, send_from_directory, g
from werkzeug.contrib.atom import AtomFeed
from urllib.parse import urljoin
from legendarium.formatter import descriptive_short_format

from . import main
from webapp import babel
from webapp import cache
from webapp import controllers
from webapp.utils import utils
from webapp.utils.caching import cache_key_with_lang, cache_key_with_lang_with_qs
from webapp import forms

logger = logging.getLogger(__name__)

JOURNAL_UNPUBLISH = _("O periódico está indisponível por motivo de: ")
ISSUE_UNPUBLISH = _("O número está indisponível por motivo de: ")
ARTICLE_UNPUBLISH = _("O artigo está indisponível por motivo de: ")


def url_external(endpoint, **kwargs):
    url = url_for(endpoint, **kwargs)
    return urljoin(request.url_root, url)


@main.before_app_request
def add_collection_to_g():
    if not hasattr(g, 'collection'):
        try:
            collection = controllers.get_current_collection()
            setattr(g, 'collection', collection)
        except Exception:
            # discutir o que fazer aqui
            setattr(g, 'collection', {})


@main.before_app_request
def add_forms_to_g():
    setattr(g, 'email_share', forms.EmailShareForm())
    setattr(g, 'email_contact', forms.ContactForm())
    setattr(g, 'error', forms.ErrorForm())


@babel.localeselector
def get_locale():
    langs = current_app.config.get('LANGUAGES')
    lang_from_headers = request.accept_languages.best_match(list(langs.keys()))

    if 'lang' not in list(session.keys()):
        session['lang'] = lang_from_headers

    if not lang_from_headers and not session['lang']:
        # Caso não seja possível detectar o idioma e não tenhamos a chave lang
        # no seção, fixamos o idioma padrão.
        session['lang'] = current_app.config.get('BABEL_DEFAULT_LOCALE')

    return session['lang']


@main.route('/set_locale/<string:lang_code>/')
def set_locale(lang_code):
    langs = current_app.config.get('LANGUAGES')

    if lang_code not in list(langs.keys()):
        abort(400, _('Código de idioma inválido'))

    # salvar o lang code na sessão
    session['lang'] = lang_code

    return redirect(request.referrer)


def get_lang_from_session():
    """
    Tenta retornar o idioma da seção, caso não consiga retorna
    BABEL_DEFAULT_LOCALE.
    """
    try:
        return session['lang']
    except KeyError:
        return current_app.config.get('BABEL_DEFAULT_LOCALE')


@main.route('/')
@cache.cached(key_prefix=cache_key_with_lang)
def index():
    language = session.get('lang', get_locale())
    news = controllers.get_latest_news_by_lang(language)

    tweets = controllers.get_collection_tweets()
    press_releases = controllers.get_press_releases({'language': language})

    urls = {
        'downloads': '{0}/w/accesses?collection={1}'.format(
            current_app.config['METRICS_URL'],
            current_app.config['OPAC_COLLECTION']),
        'references': '{0}/w/publication/size?collection={1}'.format(
            current_app.config['METRICS_URL'],
            current_app.config['OPAC_COLLECTION']),
        'other': '{0}/?collection={1}'.format(
            current_app.config['METRICS_URL'],
            current_app.config['OPAC_COLLECTION'])
    }

    context = {
        'news': news,
        'urls': urls,
        'tweets': tweets,
        'press_releases': press_releases,
        'journals': controllers.get_journals(query_filter="current", order_by="-last_issue.year")
    }

    return render_template("collection/index.html", **context)


# ##################################Collection###################################


@main.route('/journals/')
@cache.cached(key_prefix=cache_key_with_lang)
def collection_list():
    return render_template("collection/list_journal.html")


@main.route('/journals/feed/')
@cache.cached(key_prefix=cache_key_with_lang)
def collection_list_feed():
    language = session.get('lang', get_locale())
    collection = controllers.get_current_collection()

    title = 'SciELO - %s - %s' % (collection.name, _('Últimos periódicos inseridos na coleção'))
    subtitle = _('10 últimos periódicos inseridos na coleção %s' % collection.name)

    feed = AtomFeed(title,
                    subtitle=subtitle,
                    feed_url=request.url, url=request.url_root)

    journals = controllers.get_journals_paginated(
        title_query='', page=1, order_by='-created', per_page=10)

    if not journals.items:
        feed.add('Nenhum periódico encontrado',
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


@main.route("/about/", methods=['GET'])
@main.route('/about/<string:slug_name>/<string:lang>', methods=['GET'])
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def about_collection(slug_name=None, lang=None):
    language = lang or session.get('lang', get_locale())

    context = {}
    page = None
    if slug_name:
        # caso seja uma página
        page = controllers.get_page_by_slug_name(slug_name, language)
        if not page:
            abort(404, _('Página não encontrada'))
        context['page'] = page
    else:
        # caso não seja uma página é uma lista
        pages = controllers.get_pages_by_lang(language)
        context['pages'] = pages

    return render_template("collection/about.html", **context)


# ###################################Journal#####################################


@main.route('/scielo.php/')
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def router_legacy():

    script_php = request.args.get('script', None)
    pid = request.args.get('pid', None)
    allowed_scripts = [
        'sci_serial', 'sci_issuetoc', 'sci_arttext', 'sci_abstract', 'sci_issues', 'sci_pdf'
    ]
    if (script_php is not None) and (script_php in allowed_scripts) and not pid:
        # se tem pelo menos um param: pid ou script_php
        abort(400, _(u'Requsição inválida ao tentar acessar o artigo com pid: %s' % pid))
    elif script_php and pid:

        if script_php == 'sci_serial':
            # pid = issn
            journal = controllers.get_journal_by_issn(pid)

            if not journal:
                abort(404, _('Periódico não encontrado'))

            if not journal.is_public:
                abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

            return journal_detail(journal.url_segment)

        elif script_php == 'sci_issuetoc':

            issue = controllers.get_issue_by_pid(pid)

            if not issue:
                abort(404, _('Número não encontrado'))

            if not issue.is_public:
                abort(404, ISSUE_UNPUBLISH + _(issue.unpublish_reason))

            if not issue.journal.is_public:
                abort(404, JOURNAL_UNPUBLISH + _(issue.journal.unpublish_reason))

            return issue_toc(issue.journal.url_segment, issue.url_segment)

        elif script_php == 'sci_arttext' or script_php == 'sci_abstract':

            article = controllers.get_article_by_pid(pid)

            if not article:
                article = controllers.get_article_by_oap_pid(pid)

            if not article:
                abort(404, _('Artigo não encontrado'))

            if not article.is_public:
                abort(404, ARTICLE_UNPUBLISH + _(article.unpublish_reason))

            if not article.issue.is_public:
                abort(404, ISSUE_UNPUBLISH + _(article.issue.unpublish_reason))

            if not article.journal.is_public:
                abort(404, JOURNAL_UNPUBLISH + _(article.journal.unpublish_reason))

            return article_detail(article.journal.url_segment,
                                  article.issue.url_segment,
                                  article.url_segment)

        elif script_php == 'sci_issues':

            journal = controllers.get_journal_by_issn(pid)

            if not journal:
                abort(404, _('Periódico não encontrado'))

            if not journal.is_public:
                abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

            return issue_grid(journal.url_segment)

        elif script_php == 'sci_pdf':
            # accesso ao pdf do artigo:
            article = controllers.get_article_by_pid(pid)

            if not article:
                article = controllers.get_article_by_oap_pid(pid)

            if not article:
                abort(404, _('Artigo não encontrado'))

            if not article.is_public:
                abort(404, ARTICLE_UNPUBLISH + _(article.unpublish_reason))

            if not article.issue.is_public:
                abort(404, ISSUE_UNPUBLISH + _(article.issue.unpublish_reason))

            if not article.journal.is_public:
                abort(404, JOURNAL_UNPUBLISH + _(article.journal.unpublish_reason))

            return article_detail_pdf(
                article.journal.url_segment,
                article.issue.url_segment,
                article.url_segment)

        else:
            abort(400, _(u'Requsição inválida ao tentar acessar o artigo com pid: %s' % pid))

    else:
        return redirect('/')


@main.route('/journal/<string:url_seg>/')
@cache.cached(key_prefix=cache_key_with_lang)
def journal_detail(url_seg):
    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _('Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    # todo: ajustar para que seja só noticias relacionadas ao periódico
    language = session.get('lang', get_locale())
    news = controllers.get_latest_news_by_lang(language)

    # A ordenação padrão da função ``get_issues_by_jid``: "-year", "-volume", "order"
    issues = controllers.get_issues_by_jid(journal.id, is_public=True)

    # A lista de números deve ter mais do que 1 item para que possamos tem
    # anterior e próximo
    if len(issues) >= 2:
        previous_issue = issues[1]
    else:
        previous_issue = None

    # Press releases
    press_releases = controllers.get_press_releases({
        'journal': journal,
        'language': language})

    # Lista de seções
    # Mantendo sempre o idioma inglês para as seções na página incial do periódico
    if journal.last_issue:
        sections = [section for section in journal.last_issue.sections if section.language == 'en']
        recent_articles = controllers.get_recent_articles_of_issue(journal.last_issue.iid, is_public=True)
    else:
        sections = []
        recent_articles = []

    if len(issues) > 0:
        latest_issue = issues[0]
        latest_issue_legend = descriptive_short_format(
            title=latest_issue.journal.title, short_title=latest_issue.journal.short_title,
            pubdate=str(latest_issue.year), volume=latest_issue.volume, number=latest_issue.number,
            suppl=latest_issue.suppl_text, language=language[:2].lower())
    else:
        latest_issue = None
        latest_issue_legend = ''

    context = {
        'next_issue': None,
        'previous_issue': previous_issue,
        'journal': journal,
        'press_releases': press_releases,
        'recent_articles': recent_articles,
        # o primiero item da lista é o último número.
        # condicional para verificar se issues contém itens
        'last_issue': latest_issue,
        'latest_issue_legend': latest_issue_legend,
        'sections': sections if sections else None,
        'news': news
    }

    return render_template("journal/detail.html", **context)


@main.route('/journal/<string:url_seg>/feed/')
@cache.cached(key_prefix=cache_key_with_lang)
def journal_feed(url_seg):
    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _('Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    issues = controllers.get_issues_by_jid(journal.jid, is_public=True)
    last_issue = issues[0] if issues else None
    articles = controllers.get_articles_by_iid(last_issue.iid, is_public=True)

    feed = AtomFeed(journal.title,
                    feed_url=request.url,
                    url=request.url_root,
                    subtitle=utils.get_label_issue(last_issue))

    feed_language = session.get('lang', get_locale())
    feed_language = feed_language[:2].lower()

    for article in articles:

        # ######### TODO: Revisar #########
        article_lang = feed_language
        if feed_language not in article.languages:
            article_lang = article.original_language

        feed.add(article.title or _('Artigo sem título'),
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


@main.route("/journal/<string:url_seg>/about/", methods=['GET'])
@cache.cached(key_prefix=cache_key_with_lang)
def about_journal(url_seg):
    language = session.get('lang', get_locale())

    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _('Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    # A ordenação padrão da função ``get_issues_by_jid``: "-year", "-volume", "order"
    issues = controllers.get_issues_by_jid(journal.id, is_public=True)

    # A lista de números deve ter mais do que 1 item para que possamos tem
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
        # o primiero item da lista é o último número.
        # condicional para verificar se issues contém itens
        'last_issue': issues[0] if issues else None,
    }

    if page:
        context['content'] = page.content
        if page.updated_at:
            context['page_updated_at'] = page.updated_at

    return render_template("journal/about.html", **context)


@main.route("/journals/search/alpha/ajax/", methods=['GET', ])
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def journals_search_alpha_ajax():

    if not request.is_xhr:
        abort(400, _('Requisição inválida. Deve ser por ajax'))

    query = request.args.get('query', '', type=str)
    query_filter = request.args.get('query_filter', '', type=str)
    page = request.args.get('page', 1, type=int)
    lang = get_lang_from_session()[:2].lower()
    response_data = controllers.get_alpha_list_from_paginated_journals(
        title_query=query, query_filter=query_filter, page=page, lang=lang)

    return jsonify(response_data)


@main.route("/journals/search/group/by/filter/ajax/", methods=['GET'])
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def journals_search_by_theme_ajax():

    if not request.is_xhr:
        abort(400, _('Requisição inválida. Deve ser por ajax'))

    query = request.args.get('query', '', type=str)
    query_filter = request.args.get('query_filter', '', type=str)
    filter = request.args.get('filter', 'areas', type=str)
    lang = get_lang_from_session()[:2].lower()

    if filter == 'areas':
        objects = controllers.get_journals_grouped_by('subject_categories', query, query_filter=query_filter, lang=lang)
    elif filter == 'wos':
        objects = controllers.get_journals_grouped_by('index_at', query, query_filter=query_filter, lang=lang)
    elif filter == 'publisher':
        objects = controllers.get_journals_grouped_by('publisher_name', query, query_filter=query_filter, lang=lang)
    else:
        return jsonify({
            'error': 401,
            'message': _('Parámetro "filter" é inválido, deve ser "areas", "wos" ou "publisher".')
        })
    return jsonify(objects)


@main.route("/journals/download/<string:list_type>/<string:extension>/", methods=['GET', ])
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def download_journal_list(list_type, extension):
    if extension.lower() not in ['csv', 'xls']:
        abort(401, _('Parámetro "extension" é inválido, deve ser "csv" ou "xls".'))
    elif list_type.lower() not in ['alpha', 'areas', 'wos', 'publisher']:
        abort(401, _('Parámetro "list_type" é inválido, deve ser: "alpha", "areas", "wos" ou "publisher".'))
    else:
        if extension.lower() == 'xls':
            mimetype = 'application/vnd.ms-excel'
        else:
            mimetype = 'text/csv'
        query = request.args.get('query', '', type=str)
        data = controllers.get_journal_generator_for_csv(list_type=list_type,
                                                         title_query=query,
                                                         extension=extension.lower())
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = 'journals_%s_%s.%s' % (list_type, timestamp, extension)
        response = Response(data, mimetype=mimetype)
        response.headers['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


@main.route("/<string:url_seg>/contact", methods=['POST'])
def contact(url_seg):

    if not request.is_xhr:
        abort(403, _('Requisição inválida, deve ser ajax.'))

    if utils.is_recaptcha_valid(request):

        form = forms.ContactForm(request.form)

        journal = controllers.get_journal_by_url_seg(url_seg)

        if not journal.enable_contact:
            abort(403, _('Periódico não permite envio de email.'))

        recipients = journal.editor_email

        if form.validate():
            sent, message = controllers.send_email_contact(recipients,
                                                           form.data['name'],
                                                           form.data['your_email'],
                                                           form.data['message'])

            return jsonify({'sent': sent, 'message': str(message),
                            'fields': [key for key in form.data.keys()]})

        else:
            return jsonify({'sent': False, 'message': form.errors,
                            'fields': [key for key in form.data.keys()]})

    else:
        abort(400, _('Requisição inválida, captcha inválido.'))


@main.route("/form_contact/<string:url_seg>/", methods=['GET'])
def form_contact(url_seg):
    journal = controllers.get_journal_by_url_seg(url_seg)
    if not journal:
        abort(404, _('Periódico não encontrado'))

    context = {
        'journal': journal
    }
    return render_template("journal/includes/contact_form.html", **context)


# ###################################Issue#######################################


@main.route('/grid/<string:url_seg>/')
@cache.cached(key_prefix=cache_key_with_lang)
def issue_grid(url_seg):
    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _('Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    # idioma da sessão
    language = session.get('lang', get_locale())

    # A ordenação padrão da função ``get_issues_by_jid``: "-year", "-volume", "-order"
    issues_data = controllers.get_issues_for_grid_by_jid(journal.id, is_public=True)
    latest_issue = issues_data['last_issue']
    if latest_issue:
        latest_issue_legend = descriptive_short_format(
            title=latest_issue.journal.title, short_title=latest_issue.journal.short_title,
            pubdate=str(latest_issue.year), volume=latest_issue.volume, number=latest_issue.number,
            suppl=latest_issue.suppl_text, language=language[:2].lower())
    else:
        latest_issue_legend = None

    context = {
        'journal': journal,
        'next_issue': None,
        'previous_issue': issues_data['previous_issue'],
        'last_issue': issues_data['last_issue'],
        'latest_issue_legend': latest_issue_legend,
        'volume_issue': issues_data['volume_issue'],
        'ahead': issues_data['ahead'],
        'result_dict': issues_data['ordered_for_grid'],
    }

    return render_template("issue/grid.html", **context)


@main.route('/toc/<string:url_seg>/<regex("\d{4}\.(\w+[-\.]?\w+[-\.]?)"):url_seg_issue>/')
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def issue_toc(url_seg, url_seg_issue):
    # idioma da sessão
    language = session.get('lang', get_locale())

    section_filter = request.args.get('section', '', type=str)

    issue = controllers.get_issue_by_url_seg(url_seg, url_seg_issue)

    if issue and issue.journal:
        issue_legend = descriptive_short_format(
            title=issue.journal.title, short_title=issue.journal.short_title,
            pubdate=str(issue.year), volume=issue.volume, number=issue.number,
            suppl=issue.suppl_text, language=language[:2].lower())

    if not issue:
        abort(404, _('Número não encontrado'))

    if not issue.is_public:
        abort(404, ISSUE_UNPUBLISH + _(issue.unpublish_reason))

    if not issue.journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(issue.journal.unpublish_reason))

    journal = issue.journal
    articles = controllers.get_articles_by_iid(issue.iid, is_public=True)

    if articles:
        sections = list(articles.item_frequencies('section').keys())
        sections = sorted([k for k in sections if k is not None])
    else:
        sections = []

    issues = controllers.get_issues_by_jid(journal.id, is_public=True)

    if section_filter != '':
        articles = articles.filter(section__iexact=section_filter)

    issue_list = [_issue for _issue in issues]

    previous_issue = utils.get_prev_issue(issue_list, issue)
    next_issue = utils.get_next_issue(issue_list, issue)

    for article in articles:
        article_text_languages = [doc['lang'] for doc in article.htmls]
        article_pdf_languages = [(doc['lang'], doc['url']) for doc in article.pdfs]

        setattr(article, "article_text_languages", article_text_languages)
        setattr(article, "article_pdf_languages", article_pdf_languages)

    context = {
        'next_issue': next_issue,
        'previous_issue': previous_issue,
        'journal': journal,
        'issue': issue,
        'issue_legend': issue_legend,
        'articles': articles,
        'sections': sections,
        'section_filter': section_filter,
        # o primiero item da lista é o último número.
        'last_issue': issues[0] if issues else None
    }

    return render_template("issue/toc.html", **context)


@main.route('/feed/<string:url_seg>/<regex("\d{4}\.(\w+[-\.]?\w+[-\.]?)"):url_seg_issue>/')
@cache.cached(key_prefix=cache_key_with_lang)
def issue_feed(url_seg, url_seg_issue):
    issue = controllers.get_issue_by_url_seg(url_seg, url_seg_issue)

    if not issue:
        abort(404, _('Número não encontrado'))

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

    feed_language = session.get('lang', get_locale())

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

# ##################################Article######################################


@main.route('/article/<regex("S\d{4}-\d{3}[0-9xX][0-2][0-9]{3}\d{4}\d{5}"):pid>/')
@cache.cached(key_prefix=cache_key_with_lang)
def article_detail_pid(pid):

    article = controllers.get_article_by_pid(pid)

    if not article:
        abort(404, _('Artigo não encontrado'))

    return redirect(url_for('main.article_detail',
                            url_seg=article.journal.acronym,
                            url_seg_issue=article.issue.url_segment,
                            url_seg_article=article.url_segment))


@main.route('/article/<string:url_seg>/<regex("\d{4}\.(\w+[-\.]?\w+[-\.]?)"):url_seg_issue>/<string:url_seg_article>/')
@main.route('/article/<string:url_seg>/<regex("\d{4}\.(\w+[-\.]?\w+[-\.]?)"):url_seg_issue>/<string:url_seg_article>/<regex("(?:\w{2})"):lang_code>/')
@main.route('/article/<string:url_seg>/<regex("\d{4}\.(\w+[-\.]?\w+[-\.]?)"):url_seg_issue>/<regex("(.*)"):url_seg_article>/')
@main.route('/article/<string:url_seg>/<regex("\d{4}\.(\w+[-\.]?\w+[-\.]?)"):url_seg_issue>/<regex("(.*)"):url_seg_article>/<regex("(?:\w{2})"):lang_code>/')
@cache.cached(key_prefix=cache_key_with_lang)
def article_detail(url_seg, url_seg_issue, url_seg_article, lang_code=''):

    issue = controllers.get_issue_by_url_seg(url_seg, url_seg_issue)

    if not issue:
        abort(404, _('Issue não encontrado'))

    article = controllers.get_article_by_issue_article_seg(issue.iid, url_seg_article)

    if not article:
        abort(404, _('Artigo não encontrado'))

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

    pdf_urls_path = []

    if article.pdfs:
        try:
            pdf_urls = [pdf['url'] for pdf in article.pdfs]

            if not pdf_urls:
                abort(404, _('PDF do Artigo não encontrado'))
            else:
                pdf_urls_parsed = list(map(urlparse, pdf_urls))
                pdf_urls_path = [pdf.path for pdf in pdf_urls_parsed]

        except Exception:
            abort(404, _('PDF do Artigo não encontrado'))

    html_article = None

    if article.htmls:
        try:
            html_url = [html for html in article.htmls if html['lang'] == lang_code]

            if len(html_url) != 1:
                abort(404, _('HTML do Artigo não encontrado'))
            else:
                html_url = html_url[0]['url']

            if html_url.startswith('http'):  # http:// ou https://
                html_url_parsed = urlparse(html_url)
                html_full_ssm_url = current_app.config['SSM_BASE_URI'] + html_url_parsed.path
            else:
                html_full_ssm_url = current_app.config['SSM_BASE_URI'] + html_url

            # Obtemos o html do SSM
            try:
                result = requests.get(html_full_ssm_url)
            except requests.exceptions.RequestException:
                abort(404, _('HTML do Artigo não encontrado ou indisponível'))
            else:
                if result.status_code == 200 and len(result.content) > 0:

                    # Criamos um objeto do tip soup
                    soup = BeautifulSoup(result.content.decode('utf-8'), 'html.parser')

                    # Fatiamos o HTML pelo div com class: articleTxt
                    html_article = soup.find('div', {'id': 'standalonearticle'})
                else:
                    abort(404, _('Artigo não encontrado'))

        except IndexError:
            abort(404, _('Artigo não encontrado'))

    context = {
        'next_article': next_article,
        'previous_article': previous_article,
        'article': article,
        'journal': journal,
        'issue': issue,
        'html': html_article,
        'pdfs': article.pdfs,
        'pdf_urls_path': pdf_urls_path,
        'article_lang': lang_code,
        'LANG_NAMES': current_app.config.get('LANG_NAMES'),
    }

    return render_template("article/detail.html", **context)


@main.route('/readcube/epdf/')
@main.route('/readcube/epdf.php')
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def article_epdf():
    doi = request.args.get('doi', None, type=str)
    pid = request.args.get('pid', None, type=str)
    pdf_path = request.args.get('pdf_path', None, type=str)
    lang = request.args.get('lang', None, type=str)

    if not all([doi, pid, pdf_path, lang]):
        abort(400, _('Parâmetros insuficientes para obter o EPDF do artigo'))
    else:
        context = {
            'doi': doi,
            'pid': pid,
            'pdf_path': pdf_path,
            'lang': lang,
        }
        return render_template("article/epdf.html", **context)


@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def get_content_from_ssm(resource_ssm_media_path):
    resource_ssm_full_url = current_app.config['SSM_BASE_URI'] + resource_ssm_media_path
    try:
        ssm_response = requests.get(resource_ssm_full_url.strip())
    except Exception:
        abort(404, _('Recruso não encontrado'))
    else:
        if ssm_response.status_code == 200 and len(ssm_response.content) > 0:
            return Response(ssm_response.content, mimetype=ssm_response.headers['Content-Type'])
        else:
            abort(404, _('Recurso não encontrado'))


@main.route('/media/assets/<regex("(.*)"):relative_media_path>')
@cache.cached(key_prefix=cache_key_with_lang)
def media_assets_proxy(relative_media_path):
    resource_ssm_path = '{ssm_media_path}{resource_path}'.format(
        ssm_media_path=current_app.config['SSM_MEDIA_PATH'],
        resource_path=relative_media_path)
    return get_content_from_ssm(resource_ssm_path)


@main.route('/article/ssm/content/raw/')
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def article_ssm_content_raw():
    resource_ssm_path = request.args.get('resource_ssm_path', None)
    if not resource_ssm_path:
        raise abort(404, _('Recurso do Artigo não encontrado. Caminho inválido!'))
    else:
        return get_content_from_ssm(resource_ssm_path)


@main.route('/pdf/<string:url_seg>/<regex("\d{4}\.(\w+[-\.]?\w+[-\.]?)"):url_seg_issue>/<string:url_seg_article>')
@main.route('/pdf/<string:url_seg>/<regex("\d{4}\.(\w+[-\.]?\w+[-\.]?)"):url_seg_issue>/<string:url_seg_article>/<regex("(?:\w{2})"):lang_code>')
@main.route('/pdf/<string:url_seg>/<regex("\d{4}\.(\w+[-\.]?\w+[-\.]?)"):url_seg_issue>/<regex("(.*)"):url_seg_article>')
@main.route('/pdf/<string:url_seg>/<regex("\d{4}\.(\w+[-\.]?\w+[-\.]?)"):url_seg_issue>/<regex("(.*)"):url_seg_article>/<regex("(?:\w{2})"):lang_code>')
@cache.cached(key_prefix=cache_key_with_lang)
def article_detail_pdf(url_seg, url_seg_issue, url_seg_article, lang_code=''):
    issue = controllers.get_issue_by_url_seg(url_seg, url_seg_issue)

    if not issue:
        abort(404, _('Issue não encontrado'))

    article = controllers.get_article_by_issue_article_seg(issue.iid, url_seg_article)

    if not article:
        abort(404, _('Artigo não encontrado'))

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

    pdf_ssm_path = None

    if article.pdfs:
        try:
            pdf_url = [pdf for pdf in article.pdfs if pdf['lang'] == lang_code]

            if len(pdf_url) != 1:
                abort(404, _('PDF do Artigo não encontrado'))
            else:
                pdf_url = pdf_url[0]['url']

            pdf_url_parsed = urlparse(pdf_url)
            pdf_ssm_path = pdf_url_parsed.path

        except Exception:
            abort(404, _('PDF do Artigo não encontrado'))
    else:
        abort(404, _('PDF do Artigo não encontrado'))

    context = {
        'next_article': next_article,
        'previous_article': previous_article,
        'article': article,
        'journal': journal,
        'issue': issue,
        'pdf_ssm_path': pdf_ssm_path,
        'pdfs': article.pdfs,
        'article_lang': lang_code
    }

    return render_template("article/detail_pdf.html", **context)


@main.route('/pdf/<string:journal_acron>/<string:issue_info>/<string:pdf_filename>.pdf')
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def router_legacy_pdf(journal_acron, issue_info, pdf_filename):
    language = session.get('lang', get_locale())
    pdf_filename = '%s.pdf' % pdf_filename

    journal = controllers.get_journal_by_acron(journal_acron)

    if not journal:
        abort(404, _('Periódico não encontrado'))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    # procuramos o issue filtrando pelo campo: assets_code e o journal
    issue = controllers.get_issue_by_journal_and_assets_code(assets_code=issue_info, journal=journal)

    if not issue:
        abort(404, _('Número não encontrado'))

    if not issue.is_public:
        abort(404, ISSUE_UNPUBLISH + _(issue.unpublish_reason))

    pdf_lang = language

    # procuramos entre os artigos, qual tem um pdf nesse idioma com esse filename
    article_match = None
    for article in controllers.get_articles_by_iid(iid=issue.iid):
        if article.pdfs:
            for pdf in article.pdfs:
                if pdf['url'].endswith(pdf_filename):
                    article_match = article
                    pdf_lang = pdf['lang']
                    break

    if article_match is None:
        abort(404, _('PDF do artigo não foi encontrado'))
    else:
        return article_detail_pdf(
            url_seg=journal.url_segment,
            url_seg_issue=issue.url_segment,
            url_seg_article=article_match.url_segment, lang_code=pdf_lang)

# ##################################Search#######################################


@main.route("/metasearch/", methods=['GET'])
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def metasearch():
    url = request.args.get('url', current_app.config['URL_SEARCH'], type=str)
    params = {}
    for k, v in list(request.args.items()):
        if k != 'url':
            params[k] = v
    xml = utils.do_request(url, request.args)
    return Response(xml, mimetype='text/xml')

# ###############################E-mail share####################################


@main.route("/email_share_ajax/", methods=['POST'])
def email_share_ajax():

    if not request.is_xhr:
        abort(400, _('Requisição inválida.'))

    form = forms.EmailShareForm(request.form)

    if form.validate():
        recipients = [email.strip() for email in form.data['recipients'].split(';') if email.strip() != '']

        sent, message = controllers.send_email_share(form.data['your_email'],
                                                     recipients,
                                                     form.data['share_url'],
                                                     form.data['subject'],
                                                     form.data['comment'])

        return jsonify({'sent': sent, 'message': str(message),
                        'fields': [key for key in form.data.keys()]})

    else:
        return jsonify({'sent': False, 'message': form.errors,
                        'fields': [key for key in form.data.keys()]})


@main.route("/form_mail/", methods=['GET'])
def email_form():
    context = {'url': request.args.get('url')}
    return render_template("email/email_form.html", **context)


@main.route("/email_error_ajax/", methods=['POST'])
def email_error_ajax():

    if not request.is_xhr:
        abort(400, _('Requisição inválida.'))

    form = forms.ErrorForm(request.form)

    if form.validate():

        recipients = [email.strip() for email in current_app.config.get('EMAIL_ACCOUNTS_RECEIVE_ERRORS') if email.strip() != '']

        sent, message = controllers.send_email_error(form.data['name'],
                                                     form.data['your_email'],
                                                     recipients,
                                                     form.data['url'],
                                                     form.data['error_type'],
                                                     form.data['message'])

        return jsonify({'sent': sent, 'message': str(message),
                        'fields': [key for key in form.data.keys()]})

    else:
        return jsonify({'sent': False, 'message': form.errors,
                        'fields': [key for key in form.data.keys()]})


@main.route("/error_mail/", methods=['GET'])
def error_form():
    context = {'url': request.args.get('url')}
    return render_template("includes/error_form.html", **context)


# ##################################Others#######################################


@main.route("/media/<path:filename>/", methods=['GET'])
@cache.cached(key_prefix=cache_key_with_lang)
def download_file_by_filename(filename):
    media_root = current_app.config['MEDIA_ROOT']
    return send_from_directory(media_root, filename)


@main.route("/img/scielo.gif", methods=['GET'])
def full_text_image():
    return send_from_directory('static', 'img/full_text_scielo_img.gif')


@main.route("/robots.txt", methods=['GET'])
def get_robots_txt_file():
    return send_from_directory('static', 'robots.txt')
