# coding: utf-8
import io
import json
import logging
import mimetypes
from collections import OrderedDict
from datetime import datetime, timedelta
from io import BytesIO
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from feedwerk.atom import AtomFeed
from flask import (
    Response,
    abort,
    current_app,
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    session,
    url_for,
)
from flask_babelex import gettext as _
from legendarium.formatter import descriptive_short_format
from lxml import etree
from opac_schema.v1.models import Article, Collection, Issue, Journal
from packtools import HTMLGenerator
from webapp import babel, cache, controllers, forms
from webapp.choices import STUDY_AREAS
from webapp.config.lang_names import display_original_lang_name
from webapp.utils import utils
from webapp.utils.caching import cache_key_with_lang, cache_key_with_lang_with_qs

from . import main

logger = logging.getLogger(__name__)

JOURNAL_UNPUBLISH = _("O periódico está indisponível por motivo de: ")
ISSUE_UNPUBLISH = _("O número está indisponível por motivo de: ")
ARTICLE_UNPUBLISH = _("O artigo está indisponível por motivo de: ")

IAHX_LANGS = dict(
    p="pt",
    e="es",
    i="en",
)


def url_external(endpoint, **kwargs):
    url = url_for(endpoint, **kwargs)
    return urljoin(request.url_root, url)


class RetryableError(Exception):
    """Erro recuperável sem que seja necessário modificar o estado dos dados
    na parte cliente, e.g., time
    etc.
    """


class NonRetryableError(Exception):
    """Erro do qual não pode ser recuperado sem modificar o estado dos dados
    na parte cliente, e.g., recurso solicitado não exite, URI inválida etc.
    """


def fetch_data(url: str, timeout: float = 2) -> bytes:
    try:
        response = requests.get(url, timeout=timeout)
    except (requests.ConnectionError, requests.Timeout) as exc:
        raise RetryableError(exc) from exc
    except (requests.InvalidSchema, requests.MissingSchema, requests.InvalidURL) as exc:
        raise NonRetryableError(exc) from exc
    else:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if 400 <= exc.response.status_code < 500:
                raise NonRetryableError(exc) from exc
            elif 500 <= exc.response.status_code < 600:
                raise RetryableError(exc) from exc
            else:
                raise

    return response.content


@main.before_app_request
def add_collection_to_g():
    if not hasattr(g, "collection"):
        try:
            collection = controllers.get_current_collection()
            setattr(g, "collection", collection)
        except Exception:
            # discutir o que fazer aqui
            setattr(g, "collection", {})


@main.after_request
def add_header(response):
    response.cache_control.max_age = current_app.config.get(
        "CACHE_CONTROL_MAX_AGE_HEADER"
    )
    response.headers["x-content-type-options"] = "nosniff"
    return response


@main.after_request
def add_language_code(response):
    language = session.get("lang", get_locale())
    response.set_cookie("language", language)
    return response


@main.before_app_request
def add_forms_to_g():
    setattr(g, "email_share", forms.EmailShareForm())
    setattr(g, "email_contact", forms.ContactForm())
    setattr(g, "error", forms.ErrorForm())


@main.before_app_request
def add_scielo_org_config_to_g():
    language = session.get("lang", get_locale())
    scielo_org_links = {
        key: url[language]
        for key, url in current_app.config.get("SCIELO_ORG_URIS", {}).items()
    }
    setattr(g, "scielo_org", scielo_org_links)


@babel.localeselector
def get_locale():
    langs = current_app.config.get("LANGUAGES")
    lang_from_headers = request.accept_languages.best_match(list(langs.keys()))

    if "lang" not in list(session.keys()):
        session["lang"] = lang_from_headers

    if not lang_from_headers and not session["lang"]:
        # Caso não seja possível detectar o idioma e não tenhamos a chave lang
        # no seção, fixamos o idioma padrão.
        session["lang"] = current_app.config.get("BABEL_DEFAULT_LOCALE")

    return session["lang"]


@main.route("/set_locale/<string:lang_code>/")
def set_locale(lang_code):
    langs = current_app.config.get("LANGUAGES")

    if lang_code not in list(langs.keys()):
        abort(400, _("Código de idioma inválido"))

    referrer = request.referrer
    hash = request.args.get("hash")
    if hash:
        referrer += "#" + hash

    # salvar o lang code na sessão
    session["lang"] = lang_code
    if referrer:
        return redirect(referrer)
    else:
        return redirect("/")


def get_lang_from_session():
    """
    Tenta retornar o idioma da seção, caso não consiga retorna
    BABEL_DEFAULT_LOCALE.
    """
    try:
        return session["lang"]
    except KeyError:
        return current_app.config.get("BABEL_DEFAULT_LOCALE")


@main.route("/")
@cache.cached(key_prefix=cache_key_with_lang)
def index():
    language = session.get("lang", get_locale())
    news = controllers.get_latest_news_by_lang(language)

    tweets = controllers.get_collection_tweets()
    press_releases = controllers.get_press_releases({"language": language})

    urls = {
        "downloads": "{0}/w/accesses?collection={1}".format(
            current_app.config["METRICS_URL"], current_app.config["OPAC_COLLECTION"]
        ),
        "references": "{0}/w/publication/size?collection={1}".format(
            current_app.config["METRICS_URL"], current_app.config["OPAC_COLLECTION"]
        ),
        "other": "{0}/?collection={1}".format(
            current_app.config["METRICS_URL"], current_app.config["OPAC_COLLECTION"]
        ),
    }

    if (
        g.collection is not None
        and isinstance(g.collection, Collection)
        and g.collection.metrics is not None
        and current_app.config["USE_HOME_METRICS"]
    ):
        g.collection.metrics.total_journal = Journal.objects.filter(
            is_public=True, current_status="current"
        ).count()
        g.collection.metrics.total_article = Article.objects.filter(
            is_public=True
        ).count()

    context = {
        "news": news,
        "urls": urls,
        "tweets": tweets,
        "press_releases": press_releases,
    }

    return render_template("collection/index.html", **context)


# ##################################Collection###################################


@main.route("/journals/alpha")
@cache.cached(key_prefix=cache_key_with_lang)
def collection_list():
    allowed_filters = ["current", "no-current", ""]
    query_filter = request.args.get("status", "")

    if not query_filter in allowed_filters:
        query_filter = ""

    journals_list = [
        controllers.get_journal_json_data(journal)
        for journal in controllers.get_journals(query_filter=query_filter)
    ]

    return render_template(
        "collection/list_journal.html",
        **{"journals_list": journals_list, "query_filter": query_filter}
    )


@main.route("/journals/thematic")
@cache.cached(key_prefix=cache_key_with_lang)
def collection_list_thematic():
    allowed_query_filters = ["current", "no-current", ""]
    allowed_thematic_filters = ["areas", "wos", "publisher"]
    thematic_table = {
        "areas": "study_areas",
        "wos": "subject_categories",
        "publisher": "publisher_name",
    }
    query_filter = request.args.get("status", "")
    title_query = request.args.get("query", "")
    thematic_filter = request.args.get("filter", "areas")

    if not query_filter in allowed_query_filters:
        query_filter = ""

    if not thematic_filter in allowed_thematic_filters:
        thematic_filter = "areas"

    lang = get_lang_from_session()[:2].lower()
    objects = controllers.get_journals_grouped_by(
        thematic_table[thematic_filter],
        title_query,
        query_filter=query_filter,
        lang=lang,
    )

    return render_template(
        "collection/list_thematic.html",
        **{"objects": objects, "query_filter": query_filter, "filter": thematic_filter}
    )


@main.route("/journals/feed/")
@cache.cached(key_prefix=cache_key_with_lang)
def collection_list_feed():
    language = session.get("lang", get_locale())
    collection = controllers.get_current_collection()

    title = "SciELO - %s - %s" % (
        collection.name,
        _("Últimos periódicos inseridos na coleção"),
    )
    subtitle = _("10 últimos periódicos inseridos na coleção %s" % collection.name)

    feed = AtomFeed(
        title, subtitle=subtitle, feed_url=request.url, url=request.url_root
    )

    journals = controllers.get_journals_paginated(
        title_query="", page=1, order_by="-created", per_page=10
    )

    if not journals.items:
        feed.add("Nenhum periódico encontrado", url=request.url, updated=datetime.now())

    for journal in journals.items:
        issues = controllers.get_issues_by_jid(journal.jid, is_public=True)
        last_issue = issues[0] if issues else None

        articles = []
        if last_issue:
            articles = controllers.get_articles_by_iid(last_issue.iid, is_public=True)

        result_dict = OrderedDict()
        for article in articles:
            section = article.get_section_by_lang(language[:2])
            result_dict.setdefault(section, [])
            result_dict[section].append(article)

        context = {
            "journal": journal,
            "articles": result_dict,
            "language": language,
            "last_issue": last_issue,
        }

        feed.add(
            journal.title,
            render_template("collection/list_feed_content.html", **context),
            content_type="html",
            author=journal.publisher_name,
            url=url_external("main.journal_detail", url_seg=journal.url_segment),
            updated=journal.updated,
            published=journal.created,
        )

    return feed.get_response()


@main.route("/about/", methods=["GET"])
@main.route("/about/<string:slug_name>", methods=["GET"])
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def about_collection(slug_name=None):
    language = session.get("lang", get_locale())

    context = {}
    page = None
    if slug_name:
        # caso seja uma página
        page = controllers.get_page_by_slug_name(slug_name, language)
        if not page:
            abort(404, _("Página não encontrada"))
        context["page"] = page
    else:
        # caso não seja uma página é uma lista
        pages = controllers.get_pages_by_lang(language)
        context["pages"] = pages

    return render_template("collection/about.html", **context)


# ###################################Journal#####################################


@main.route("/scielo.php/")
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def router_legacy():
    script_php = request.args.get("script", None)
    pid = request.args.get("pid", None)
    tlng = request.args.get("tlng", None)
    allowed_scripts = [
        "sci_serial",
        "sci_issuetoc",
        "sci_arttext",
        "sci_abstract",
        "sci_issues",
        "sci_pdf",
    ]
    if (script_php is not None) and (script_php in allowed_scripts) and not pid:
        # se tem pelo menos um param: pid ou script_php
        abort(400, _("Requsição inválida ao tentar acessar o artigo com pid: %s" % pid))
    elif script_php and pid:
        if script_php == "sci_serial":
            # pid = issn
            journal = controllers.get_journal_by_issn(pid)

            if not journal:
                abort(404, _("Periódico não encontrado"))

            if not journal.is_public:
                abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

            return redirect(
                url_for("main.journal_detail", url_seg=journal.url_segment), code=301
            )

        elif script_php == "sci_issuetoc":
            issue = controllers.get_issue_by_pid(pid)

            if not issue:
                abort(404, _("Número não encontrado"))

            if not issue.is_public:
                abort(404, ISSUE_UNPUBLISH + _(issue.unpublish_reason))

            if not issue.journal.is_public:
                abort(404, JOURNAL_UNPUBLISH + _(issue.journal.unpublish_reason))

            if issue.url_segment and "ahead" in issue.url_segment:
                return redirect(url_for("main.aop_toc", url_seg=url_seg), code=301)

            return redirect(
                url_for(
                    "main.issue_toc",
                    url_seg=issue.journal.url_segment,
                    url_seg_issue=issue.url_segment,
                ),
                301,
            )

        elif script_php == "sci_arttext" or script_php == "sci_abstract":
            article = controllers.get_article_by_pid_v2(pid)
            if not article:
                abort(404, _("Artigo não encontrado"))

            # 'abstract' or None (not False, porque False converterá a string 'False')
            part = (script_php == "sci_abstract" and "abstract") or None

            if tlng not in article.languages:
                tlng = article.original_language

            return redirect(
                url_for(
                    "main.article_detail_v3",
                    url_seg=article.journal.url_segment,
                    article_pid_v3=article.aid,
                    part=part,
                    lang=tlng,
                ),
                code=301,
            )

        elif script_php == "sci_issues":
            journal = controllers.get_journal_by_issn(pid)

            if not journal:
                abort(404, _("Periódico não encontrado"))

            if not journal.is_public:
                abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

            return redirect(
                url_for("main.issue_grid", url_seg=journal.url_segment), 301
            )

        elif script_php == "sci_pdf":
            # accesso ao pdf do artigo:
            article = controllers.get_article_by_pid_v2(pid)
            if not article:
                abort(404, _("Artigo não encontrado"))

            return redirect(
                url_for(
                    "main.article_detail_v3",
                    url_seg=article.journal.url_segment,
                    article_pid_v3=article.aid,
                    format="pdf",
                    lang=tlng,
                ),
                code=301,
            )

        else:
            abort(
                400,
                _("Requsição inválida ao tentar acessar o artigo com pid: %s" % pid),
            )

    else:
        return redirect("/")


@main.route("/<string:journal_seg>")
@main.route("/journal/<string:journal_seg>")
def journal_detail_legacy_url(journal_seg):
    return redirect(url_for("main.journal_detail", url_seg=journal_seg), code=301)


@main.route("/j/<string:url_seg>/")
@cache.cached(key_prefix=cache_key_with_lang)
def journal_detail(url_seg):
    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _("Periódico não encontrado"))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    utils.fix_journal_last_issue(journal)

    # todo: ajustar para que seja só noticias relacionadas ao periódico
    language = session.get("lang", get_locale())
    news = controllers.get_latest_news_by_lang(language)

    # Press releases
    press_releases = controllers.get_press_releases(
        {"journal": journal, "language": language}
    )

    # Lista de seções
    # Mantendo sempre o idioma inglês para as seções na página incial do periódico
    if journal.last_issue and journal.current_status == "current":
        sections = [
            section
            for section in journal.last_issue.sections
            if section.language == "en"
        ]
        recent_articles = controllers.get_recent_articles_of_issue(
            journal.last_issue.iid, is_public=True
        )
    else:
        sections = []
        recent_articles = []

    latest_issue = journal.last_issue

    if latest_issue:
        latest_issue_legend = descriptive_short_format(
            title=journal.title,
            short_title=journal.short_title,
            pubdate=str(latest_issue.year),
            volume=latest_issue.volume,
            number=latest_issue.number,
            suppl=latest_issue.suppl_text,
            language=language[:2].lower(),
        )
    else:
        latest_issue_legend = ""

    journal_metrics = controllers.get_journal_metrics(journal)

    context = {
        "journal": journal,
        "press_releases": press_releases,
        "recent_articles": recent_articles,
        "journal_study_areas": [
            STUDY_AREAS.get(study_area.upper()) for study_area in journal.study_areas
        ],
        # o primiero item da lista é o último número.
        # condicional para verificar se issues contém itens
        "last_issue": latest_issue,
        "latest_issue_legend": latest_issue_legend,
        "sections": sections if sections else None,
        "news": news,
        "journal_metrics": journal_metrics,
    }

    return render_template("journal/detail.html", **context)


@main.route("/journal/<string:url_seg>/feed/")
@cache.cached(key_prefix=cache_key_with_lang)
def journal_feed(url_seg):
    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _("Periódico não encontrado"))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    issues = controllers.get_issues_by_jid(journal.jid, is_public=True)
    last_issue = issues[0] if issues else None
    articles = controllers.get_articles_by_iid(last_issue.iid, is_public=True)

    feed = AtomFeed(
        journal.title,
        feed_url=request.url,
        url=request.url_root,
        subtitle=utils.get_label_issue(last_issue),
    )

    feed_language = session.get("lang", get_locale())
    feed_language = feed_language[:2].lower()

    for article in articles:
        # ######### TODO: Revisar #########
        article_lang = feed_language
        if feed_language not in article.languages:
            article_lang = article.original_language

        feed.add(
            article.title or _("Artigo sem título"),
            render_template("issue/feed_content.html", article=article),
            content_type="html",
            id=article.doi or article.pid,
            author=article.authors,
            url=url_external(
                "main.article_detail_v3",
                url_seg=journal.url_segment,
                article_pid_v3=article.aid,
                lang=article_lang,
            ),
            updated=journal.updated,
            published=journal.created,
        )

    return feed.get_response()


@main.route("/journal/<string:url_seg>/about/", methods=["GET"])
@cache.cached(key_prefix=cache_key_with_lang)
def about_journal(url_seg):
    language = session.get("lang", get_locale())

    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _("Periódico não encontrado"))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    latest_issue = utils.fix_journal_last_issue(journal)

    if latest_issue:
        latest_issue_legend = descriptive_short_format(
            title=journal.title,
            short_title=journal.short_title,
            pubdate=str(latest_issue.year),
            volume=latest_issue.volume,
            number=latest_issue.number,
            suppl=latest_issue.suppl_text,
            language=language[:2].lower(),
        )
    else:
        latest_issue_legend = None

    page = controllers.get_page_by_journal_acron_lang(journal.acronym, language)

    context = {
        "journal": journal,
        "latest_issue_legend": latest_issue_legend,
        "last_issue": latest_issue,
        "journal_study_areas": [
            STUDY_AREAS.get(study_area.upper()) for study_area in journal.study_areas
        ],
    }

    if page:
        context["content"] = page.content
        if page.updated_at:
            context["page_updated_at"] = page.updated_at

    return render_template("journal/about.html", **context)


@main.route(
    "/journals/search/alpha/ajax/",
    methods=[
        "GET",
    ],
)
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def journals_search_alpha_ajax():
    if not request.headers.get("X-Requested-With"):
        abort(400, _("Requisição inválida. Deve ser por ajax"))

    query = request.args.get("query", "", type=str)
    query_filter = request.args.get("query_filter", "", type=str)
    page = request.args.get("page", 1, type=int)
    lang = get_lang_from_session()[:2].lower()

    response_data = controllers.get_alpha_list_from_paginated_journals(
        title_query=query, query_filter=query_filter, page=page, lang=lang
    )

    return jsonify(response_data)


@main.route("/journals/search/group/by/filter/ajax/", methods=["GET"])
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def journals_search_by_theme_ajax():
    if not request.headers.get("X-Requested-With"):
        abort(400, _("Requisição inválida. Deve ser por ajax"))

    query = request.args.get("query", "", type=str)
    query_filter = request.args.get("query_filter", "", type=str)
    filter = request.args.get("filter", "areas", type=str)
    lang = get_lang_from_session()[:2].lower()

    if filter == "areas":
        objects = controllers.get_journals_grouped_by(
            "study_areas", query, query_filter=query_filter, lang=lang
        )
    elif filter == "wos":
        objects = controllers.get_journals_grouped_by(
            "subject_categories", query, query_filter=query_filter, lang=lang
        )
    elif filter == "publisher":
        objects = controllers.get_journals_grouped_by(
            "publisher_name", query, query_filter=query_filter, lang=lang
        )
    else:
        return jsonify(
            {
                "error": 401,
                "message": _(
                    'Parámetro "filter" é inválido, deve ser "areas", "wos" ou "publisher".'
                ),
            }
        )
    return jsonify(objects)


@main.route(
    "/journals/download/<string:list_type>/<string:extension>/",
    methods=[
        "GET",
    ],
)
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def download_journal_list(list_type, extension):
    if extension.lower() not in ["csv", "xls"]:
        abort(401, _('Parámetro "extension" é inválido, deve ser "csv" ou "xls".'))
    elif list_type.lower() not in ["alpha", "areas", "wos", "publisher"]:
        abort(
            401,
            _(
                'Parámetro "list_type" é inválido, deve ser: "alpha", "areas", "wos" ou "publisher".'
            ),
        )
    else:
        if extension.lower() == "xls":
            mimetype = "application/vnd.ms-excel"
        else:
            mimetype = "text/csv"
        query = request.args.get("query", "", type=str)
        data = controllers.get_journal_generator_for_csv(
            list_type=list_type, title_query=query, extension=extension.lower()
        )
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = "journals_%s_%s.%s" % (list_type, timestamp, extension)
        response = Response(data, mimetype=mimetype)
        response.headers["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


@main.route("/<string:url_seg>/contact", methods=["POST"])
def contact(url_seg):
    if not request.headers.get("X-Requested-With"):
        abort(403, _("Requisição inválida, deve ser ajax."))

    if utils.is_recaptcha_valid(request):
        form = forms.ContactForm(request.form)

        journal = controllers.get_journal_by_url_seg(url_seg)

        if not journal.enable_contact:
            abort(403, _("Periódico não permite envio de email."))

        recipients = journal.editor_email

        if form.validate():
            sent, message = controllers.send_email_contact(
                recipients,
                form.data["name"],
                form.data["your_email"],
                form.data["message"],
            )

            return jsonify(
                {
                    "sent": sent,
                    "message": str(message),
                    "fields": [key for key in form.data.keys()],
                }
            )

        else:
            return jsonify(
                {
                    "sent": False,
                    "message": form.errors,
                    "fields": [key for key in form.data.keys()],
                }
            )

    else:
        abort(400, _("Requisição inválida, captcha inválido."))


@main.route("/form_contact/<string:url_seg>/", methods=["GET"])
def form_contact(url_seg):
    journal = controllers.get_journal_by_url_seg(url_seg)
    if not journal:
        abort(404, _("Periódico não encontrado"))

    context = {"journal": journal}
    return render_template("journal/includes/contact_form.html", **context)


# ###################################Issue#######################################


@main.route("/grid/<string:url_seg>/")
def issue_grid_legacy(url_seg):
    return redirect(url_for("main.issue_grid", url_seg=url_seg), 301)


@main.route("/j/<string:url_seg>/grid")
@cache.cached(key_prefix=cache_key_with_lang)
def issue_grid(url_seg):
    journal = controllers.get_journal_by_url_seg(url_seg)

    if not journal:
        abort(404, _("Periódico não encontrado"))

    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    # idioma da sessão
    language = session.get("lang", get_locale())

    # A ordenação padrão da função ``get_issues_by_jid``: "-year", "-volume", "-order"
    issues_data = controllers.get_issues_for_grid_by_jid(journal.id, is_public=True)
    latest_issue = issues_data["last_issue"]
    if latest_issue:
        latest_issue_legend = descriptive_short_format(
            title=journal.title,
            short_title=journal.short_title,
            pubdate=str(latest_issue.year),
            volume=latest_issue.volume,
            number=latest_issue.number,
            suppl=latest_issue.suppl_text,
            language=language[:2].lower(),
        )
    else:
        latest_issue_legend = None

    context = {
        "journal": journal,
        "last_issue": issues_data["last_issue"],
        "latest_issue_legend": latest_issue_legend,
        "volume_issue": issues_data["volume_issue"],
        "ahead": issues_data["ahead"],
        "result_dict": issues_data["ordered_for_grid"],
        "journal_study_areas": [
            STUDY_AREAS.get(study_area.upper()) for study_area in journal.study_areas
        ],
    }

    return render_template("issue/grid.html", **context)


@main.route("/toc/<string:url_seg>/<string:url_seg_issue>/")
def issue_toc_legacy(url_seg, url_seg_issue):
    if url_seg_issue and "ahead" in url_seg_issue:
        return redirect(url_for("main.aop_toc", url_seg=url_seg), code=301)

    return redirect(
        url_for("main.issue_toc", url_seg=url_seg, url_seg_issue=url_seg_issue),
        code=301,
    )


@main.route("/j/<string:url_seg>/i/<string:url_seg_issue>/")
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def issue_toc(url_seg, url_seg_issue):
    section_filter = None
    goto = request.args.get("goto", None, type=str)
    if goto not in ("previous", "next"):
        goto = None

    if goto in (None, "next") and "ahead" in url_seg_issue:
        # redireciona para `aop_toc`
        return redirect(url_for("main.aop_toc", url_seg=url_seg), code=301)

    # idioma da sessão
    language = session.get("lang", get_locale())

    if current_app.config["FILTER_SECTION_ENABLE"]:
        # seção dos documentos, se selecionada
        section_filter = request.args.get("section", "", type=str).upper()

    # obtém o issue
    issue = controllers.get_issue_by_url_seg(url_seg, url_seg_issue)
    if not issue:
        abort(404, _("Número não encontrado"))
    if not issue.is_public:
        abort(404, ISSUE_UNPUBLISH + _(issue.unpublish_reason))

    # obtém o journal
    journal = issue.journal
    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    # completa url_segment do last_issue
    utils.fix_journal_last_issue(journal)

    # goto_next_or_previous_issue (redireciona)
    goto_url = goto_next_or_previous_issue(
        issue, request.args.get("goto", None, type=str)
    )
    if goto_url:
        return redirect(goto_url, code=301)

    # obtém os documentos
    articles = controllers.get_articles_by_iid(issue.iid, is_public=True)
    if articles:
        # obtém TODAS as seções dos documentos deste sumário
        sections = sorted({a.section.upper() for a in articles if a.section})
    else:
        # obtém as seções dos documentos deste sumário
        sections = []

    if current_app.config["FILTER_SECTION_ENABLE"] and section_filter != "":
        # obtém somente os documentos da seção selecionada
        articles = [a for a in articles if a.section.upper() == section_filter]

    # obtém PDF e TEXT de cada documento
    has_math_content = False
    for article in articles:
        article_text_languages = [doc["lang"] for doc in article.htmls]
        article_pdf_languages = [(doc["lang"], doc["url"]) for doc in article.pdfs]
        setattr(article, "article_text_languages", article_text_languages)
        setattr(article, "article_pdf_languages", article_pdf_languages)
        if "mml:" in article.title:
            has_math_content = True

    # obtém a legenda bibliográfica
    issue_bibliographic_strip = descriptive_short_format(
        title=journal.title,
        short_title=journal.short_title,
        pubdate=str(issue.year),
        volume=issue.volume,
        number=issue.number,
        suppl=issue.suppl_text,
        language=language[:2].lower(),
    )

    context = {
        "this_page_url": url_for(
            "main.issue_toc", url_seg=url_seg, url_seg_issue=url_seg_issue
        ),
        "has_math_content": has_math_content,
        "journal": journal,
        "issue": issue,
        "issue_bibliographic_strip": issue_bibliographic_strip,
        "articles": articles,
        "sections": sections,
        "section_filter": section_filter,
        "journal_study_areas": [
            STUDY_AREAS.get(study_area.upper()) for study_area in journal.study_areas
        ],
        "last_issue": journal.last_issue,
    }
    return render_template("issue/toc.html", **context)


def goto_next_or_previous_issue(current_issue, goto_param):
    if goto_param not in ["next", "previous"]:
        return None

    all_issues = list(
        controllers.get_issues_by_jid(current_issue.journal.id, is_public=True)
    )
    if goto_param == "next":
        selected_issue = utils.get_next_issue(all_issues, current_issue)
    elif goto_param == "previous":
        selected_issue = utils.get_prev_issue(all_issues, current_issue)
    if selected_issue in (None, current_issue):
        # nao precisa redirecionar
        return None
    try:
        url_seg_issue = selected_issue.url_segment
    except AttributeError:
        return None
    else:
        return url_for(
            "main.issue_toc",
            url_seg=selected_issue.journal.url_segment,
            url_seg_issue=url_seg_issue,
        )


def get_next_or_previous_issue(current_issue, goto_param):
    if goto_param not in ["next", "previous"]:
        return current_issue

    all_issues = list(
        controllers.get_issues_by_jid(current_issue.journal.id, is_public=True)
    )
    if goto_param == "next":
        return utils.get_next_issue(all_issues, current_issue)
    return utils.get_prev_issue(all_issues, current_issue)


@main.route("/j/<string:url_seg>/aop")
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def aop_toc(url_seg):
    section_filter = request.args.get("section", "", type=str).upper()

    aop_issues = controllers.get_aop_issues(url_seg) or []
    if not aop_issues:
        abort(404, _("Artigos ahead of print não encontrados"))

    goto = request.args.get("goto", None, type=str)
    if goto == "previous":
        url = goto_next_or_previous_issue(aop_issues[-1], goto)
        if url:
            redirect(url, code=301)

    journal = aop_issues[0].journal
    if not journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(journal.unpublish_reason))

    utils.fix_journal_last_issue(journal)

    articles = []
    for aop_issue in aop_issues:
        _articles = controllers.get_articles_by_iid(aop_issue.iid, is_public=True)
        if _articles:
            articles.extend(_articles)
    if not articles:
        abort(404, _("Artigos ahead of print não encontrados"))

    sections = sorted({a.section.upper() for a in articles if a.section})
    if section_filter != "":
        articles = [a for a in articles if a.section.upper() == section_filter]

    for article in articles:
        article_text_languages = [doc["lang"] for doc in article.htmls]
        article_pdf_languages = [(doc["lang"], doc["url"]) for doc in article.pdfs]

        setattr(article, "article_text_languages", article_text_languages)
        setattr(article, "article_pdf_languages", article_pdf_languages)

    context = {
        "this_page_url": url_for("main.aop_toc", url_seg=url_seg),
        "journal": journal,
        "issue": aop_issues[0],
        "issue_bibliographic_strip": "ahead of print",
        "articles": articles,
        "sections": sections,
        "section_filter": section_filter,
        "journal_study_areas": [
            STUDY_AREAS.get(study_area.upper()) for study_area in journal.study_areas
        ],
        # o primeiro item da lista é o último número.
        "last_issue": journal.last_issue,
    }

    return render_template("issue/toc.html", **context)


@main.route("/feed/<string:url_seg>/<string:url_seg_issue>/")
@cache.cached(key_prefix=cache_key_with_lang)
def issue_feed(url_seg, url_seg_issue):
    issue = controllers.get_issue_by_url_seg(url_seg, url_seg_issue)

    if not issue:
        abort(404, _("Número não encontrado"))

    if not issue.is_public:
        abort(404, ISSUE_UNPUBLISH + _(issue.unpublish_reason))

    if not issue.journal.is_public:
        abort(404, JOURNAL_UNPUBLISH + _(issue.journal.unpublish_reason))

    journal = issue.journal
    articles = controllers.get_articles_by_iid(issue.iid, is_public=True)

    feed = AtomFeed(
        journal.title or "",
        feed_url=request.url,
        url=request.url_root,
        subtitle=utils.get_label_issue(issue),
    )

    feed_language = session.get("lang", get_locale())

    for article in articles:
        # ######### TODO: Revisar #########
        article_lang = feed_language
        if feed_language not in article.languages:
            article_lang = article.original_language

        feed.add(
            article.title or "Unknow title",
            render_template("issue/feed_content.html", article=article),
            content_type="html",
            author=article.authors,
            id=article.doi or article.pid,
            url=url_external(
                "main.article_detail_v3",
                url_seg=journal.url_segment,
                article_pid_v3=article.aid,
                lang=article_lang,
            ),
            updated=journal.updated,
            published=journal.created,
        )

    return feed.get_response()


# ##################################Article######################################


@main.route('/article/<regex("S\d{4}-\d{3}[0-9xX][0-2][0-9]{3}\d{4}\d{5}"):pid>/')
@cache.cached(key_prefix=cache_key_with_lang)
def article_detail_pid(pid):
    article = controllers.get_article_by_pid(pid)

    if not article:
        article = controllers.get_article_by_oap_pid(pid)

    if not article:
        abort(404, _("Artigo não encontrado"))

    return redirect(
        url_for(
            "main.article_detail_v3",
            url_seg=article.journal.acronym,
            article_pid_v3=article.aid,
        )
    )


def render_html_from_xml(article, lang, gs_abstract=False):
    logger.debug("Get XML: %s", article.xml)

    if current_app.config["SSM_XML_URL_REWRITE"]:
        result = fetch_data(use_ssm_url(article.xml))
    else:
        result = fetch_data(article.xml)

    xml = etree.parse(BytesIO(result))

    generator = HTMLGenerator.parse(
        xml, valid_only=False, gs_abstract=gs_abstract, output_style="website"
    )

    return generator.generate(lang), generator.languages


def render_html_from_html(article, lang):
    html_url = [html for html in article.htmls if html["lang"] == lang]

    try:
        html_url = html_url[0]["url"]
    except IndexError:
        raise ValueError("Artigo não encontrado") from None

    result = fetch_data(use_ssm_url(html_url))

    html = result.decode("utf8")

    text_languages = [html["lang"] for html in article.htmls]

    return html, text_languages


def render_html_abstract(article, lang):
    abstract_text = ""
    for abstract in article.abstracts:
        if abstract["language"] == lang:
            abstract_text = abstract["text"]
            break
    return abstract_text, article.abstract_languages


def render_html(article, lang, gs_abstract=False):
    if article.xml:
        return render_html_from_xml(article, lang, gs_abstract)
    elif article.htmls:
        if gs_abstract:
            return render_html_abstract(article, lang)
        return render_html_from_html(article, lang)
    else:
        # TODO: Corrigir os teste que esperam ter o atributo ``htmls``
        # O ideal seria levantar um ValueError.
        return "", []


# TODO: Remover assim que o valor Article.xml estiver consistente na base de
# dados
def use_ssm_url(url):
    """Normaliza a string `url` de acordo com os valores das diretivas de
    configuração OPAC_SSM_SCHEME, OPAC_SSM_DOMAIN e OPAC_SSM_PORT.

    A normalização busca obter uma URL absoluta em função de uma relativa, ou
    uma absoluta em função de uma absoluta, mas com as partes *scheme* e
    *authority* trocadas pelas definidas nas diretivas citadas anteriormente.

    Este código deve ser removido assim que o valor de Article.xml estiver
    consistente, i.e., todos os registros possuirem apenas URLs absolutas.
    """
    if url.startswith("http"):
        parsed_url = urlparse(url)
        return current_app.config["SSM_BASE_URI"] + parsed_url.path
    else:
        return current_app.config["SSM_BASE_URI"] + url


@main.route(
    "/article/<string:url_seg>/<string:url_seg_issue>/<string:url_seg_article>/"
)
@main.route(
    '/article/<string:url_seg>/<string:url_seg_issue>/<string:url_seg_article>/<regex("(?:\w{2})"):lang_code>/'
)
@main.route(
    '/article/<string:url_seg>/<string:url_seg_issue>/<regex("(.*)"):url_seg_article>/'
)
@main.route(
    '/article/<string:url_seg>/<string:url_seg_issue>/<regex("(.*)"):url_seg_article>/<regex("(?:\w{2})"):lang_code>/'
)
@cache.cached(key_prefix=cache_key_with_lang)
def article_detail(url_seg, url_seg_issue, url_seg_article, lang_code=""):
    issue = controllers.get_issue_by_url_seg(url_seg, url_seg_issue)
    if not issue:
        abort(404, _("Issue não encontrado"))

    article = controllers.get_article_by_issue_article_seg(issue.iid, url_seg_article)
    if article is None:
        article = controllers.get_article_by_aop_url_segs(
            issue.journal, url_seg_issue, url_seg_article
        )
    if article is None:
        abort(404, _("Artigo não encontrado"))

    req_params = {
        "url_seg": article.journal.acronym,
        "article_pid_v3": article.aid,
    }
    if lang_code:
        req_params["lang"] = lang_code

    return redirect(url_for("main.article_detail_v3", **req_params))


@main.route("/j/<string:url_seg>/a/<string:article_pid_v3>/")
@main.route("/j/<string:url_seg>/a/<string:article_pid_v3>/<string:part>/")
@cache.cached(key_prefix=cache_key_with_lang)
def article_detail_v3(url_seg, article_pid_v3, part=None):
    qs_lang = request.args.get("lang", type=str) or None
    qs_goto = request.args.get("goto", type=str) or None
    qs_stop = request.args.get("stop", type=str) or None
    qs_format = request.args.get("format", "html", type=str)

    gs_abstract = part == "abstract"
    if part and not gs_abstract:
        abort(404, _("Não existe '{}'. No seu lugar use '{}'").format(part, "abstract"))

    try:
        qs_lang, article = controllers.get_article(
            article_pid_v3, url_seg, qs_lang, gs_abstract, qs_goto
        )
        if qs_goto:
            return redirect(
                url_for(
                    "main.article_detail_v3",
                    url_seg=url_seg,
                    article_pid_v3=article.aid,
                    part=part,
                    format=qs_format,
                    lang=qs_lang,
                    stop=getattr(article, "stop", None),
                ),
                code=301,
            )
    except controllers.PreviousOrNextArticleNotFoundError as e:
        if gs_abstract:
            abort(404, _("Resumo inexistente"))
        abort(404, _("Artigo inexistente"))
    except (controllers.ArticleNotFoundError, controllers.ArticleJournalNotFoundError):
        abort(404, _("Artigo não encontrado"))
    except controllers.ArticleLangNotFoundError:
        return redirect(
            url_for(
                "main.article_detail_v3",
                url_seg=url_seg,
                article_pid_v3=article_pid_v3,
                format=qs_format,
            ),
            code=301,
        )
    except controllers.ArticleAbstractNotFoundError:
        abort(404, _("Recurso não encontrado"))
    except controllers.ArticleIsNotPublishedError as e:
        abort(404, "{}{}".format(ARTICLE_UNPUBLISH, e))
    except controllers.IssueIsNotPublishedError as e:
        abort(404, "{}{}".format(ISSUE_UNPUBLISH, e))
    except controllers.JournalIsNotPublishedError as e:
        abort(404, "{}{}".format(JOURNAL_UNPUBLISH, e))
    except ValueError as e:
        abort(404, str(e))

    def _handle_html():
        citation_pdf_url = None
        for pdf_data in article.pdfs:
            if pdf_data.get("lang") == qs_lang:
                citation_pdf_url = url_for(
                    "main.article_detail_v3",
                    url_seg=article.journal.url_segment,
                    article_pid_v3=article_pid_v3,
                    lang=qs_lang,
                    format="pdf",
                )
                break

        website = request.url
        if website:
            parsed_url = urlparse(request.url)
            if current_app.config["FORCE_USE_HTTPS_GOOGLE_TAGS"]:
                website = "{}://{}".format("https", parsed_url.netloc)
            else:
                website = "{}://{}".format(parsed_url.scheme, parsed_url.netloc)
        if citation_pdf_url:
            citation_pdf_url = "{}{}".format(website, citation_pdf_url)
        try:
            html, text_languages = render_html(article, qs_lang, gs_abstract)
        except (ValueError, NonRetryableError):
            abort(404, _("HTML do Artigo não encontrado ou indisponível"))
        except RetryableError:
            abort(500, _("Erro inesperado"))

        text_versions = sorted(
            [
                (
                    lang,
                    display_original_lang_name(lang),
                    url_for(
                        "main.article_detail_v3",
                        url_seg=article.journal.url_segment,
                        article_pid_v3=article_pid_v3,
                        lang=lang,
                    ),
                )
                for lang in text_languages
            ]
        )
        citation_xml_url = "{}{}".format(
            website,
            url_for(
                "main.article_detail_v3",
                url_seg=article.journal.url_segment,
                article_pid_v3=article_pid_v3,
                format="xml",
                lang=article.original_language,
            ),
        )
        context = {
            "next_article": qs_stop != "next",
            "previous_article": qs_stop != "previous",
            "article": article,
            "journal": article.journal,
            "issue": article.issue,
            "html": html,
            "citation_pdf_url": citation_pdf_url,
            "citation_xml_url": citation_xml_url,
            "article_lang": qs_lang,
            "text_versions": text_versions,
            "related_links": controllers.related_links(article),
            "gs_abstract": gs_abstract,
            "part": part,
        }
        return render_template("article/detail.html", **context)

    def _handle_pdf():
        if not article.pdfs:
            abort(404, _("PDF do Artigo não encontrado"))

        pdf_info = [pdf for pdf in article.pdfs if pdf["lang"] == qs_lang]
        if len(pdf_info) != 1:
            abort(404, _("PDF do Artigo não encontrado"))

        try:
            pdf_url = pdf_info[0]["url"]
        except (IndexError, KeyError, ValueError, TypeError):
            abort(404, _("PDF do Artigo não encontrado"))

        if pdf_url:
            return get_pdf_content(pdf_url)
        raise abort(404, _("Recurso do Artigo não encontrado. Caminho inválido!"))

    def _handle_xml():
        if current_app.config["SSM_XML_URL_REWRITE"]:
            result = fetch_data(use_ssm_url(article.xml))
        else:
            result = fetch_data(article.xml)
        response = make_response(result)
        response.headers["Content-Type"] = "application/xml"
        return response

    def _handle_csl():
        return redirect(
            url_for("main.article_cite_csl", article_id=article_pid_v3) + "?format=csl",
            code=301,
        )

    if "html" == qs_format:
        return _handle_html()
    elif "pdf" == qs_format:
        return _handle_pdf()
    elif "xml" == qs_format:
        return _handle_xml()
    elif "csl" == qs_format:
        return _handle_csl()
    else:
        abort(400, _("Formato não suportado"))


@main.route("/readcube/epdf/")
@main.route("/readcube/epdf.php")
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def article_epdf():
    doi = request.args.get("doi", None, type=str)
    pid = request.args.get("pid", None, type=str)
    pdf_path = request.args.get("pdf_path", None, type=str)
    lang = request.args.get("lang", None, type=str)

    if not all([doi, pid, pdf_path, lang]):
        abort(400, _("Parâmetros insuficientes para obter o EPDF do artigo"))
    else:
        context = {
            "doi": doi,
            "pid": pid,
            "pdf_path": pdf_path,
            "lang": lang,
        }
        return render_template("article/epdf.html", **context)


def get_pdf_content(url):
    logger.debug("Get PDF: %s", url)
    if current_app.config["SSM_ARTICLE_ASSETS_OR_RENDITIONS_URL_REWRITE"]:
        url = use_ssm_url(url)
    try:
        response = fetch_data(url)
    except NonRetryableError:
        abort(404, _("PDF não encontrado"))
    except RetryableError:
        abort(500, _("Erro inesperado"))
    else:
        mimetype, __ = mimetypes.guess_type(url)
        return Response(response, mimetype=mimetype)


@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def get_content_from_ssm(resource_ssm_media_path):
    resource_ssm_full_url = current_app.config["SSM_BASE_URI"] + resource_ssm_media_path

    url = resource_ssm_full_url.strip()
    mimetype, __ = mimetypes.guess_type(url)

    try:
        ssm_response = fetch_data(url)
    except NonRetryableError:
        abort(404, _("Recurso não encontrado"))
    except RetryableError:
        abort(500, _("Erro inesperado"))
    else:
        return Response(ssm_response, mimetype=mimetype)


@main.route('/media/assets/<regex("(.*)"):relative_media_path>')
@cache.cached(key_prefix=cache_key_with_lang)
def media_assets_proxy(relative_media_path):
    resource_ssm_path = "{ssm_media_path}{resource_path}".format(
        ssm_media_path=current_app.config["SSM_MEDIA_PATH"],
        resource_path=relative_media_path,
    )
    return get_content_from_ssm(resource_ssm_path)


@main.route("/article/ssm/content/raw/")
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def article_ssm_content_raw():
    resource_ssm_path = request.args.get("resource_ssm_path", None)
    if not resource_ssm_path:
        raise abort(404, _("Recurso do Artigo não encontrado. Caminho inválido!"))
    else:
        return get_content_from_ssm(resource_ssm_path)


@main.route("/pdf/<string:url_seg>/<string:url_seg_issue>/<string:url_seg_article>")
@main.route(
    '/pdf/<string:url_seg>/<string:url_seg_issue>/<string:url_seg_article>/<regex("(?:\w{2})"):lang_code>'
)
@main.route(
    '/pdf/<string:url_seg>/<string:url_seg_issue>/<regex("(.*)"):url_seg_article>'
)
@main.route(
    '/pdf/<string:url_seg>/<string:url_seg_issue>/<regex("(.*)"):url_seg_article>/<regex("(?:\w{2})"):lang_code>'
)
@cache.cached(key_prefix=cache_key_with_lang)
def article_detail_pdf(url_seg, url_seg_issue, url_seg_article, lang_code=""):
    """
    Padrões esperados:
        `/pdf/csc/2021.v26suppl1/2557-2558`
        `/pdf/csc/2021.v26suppl1/2557-2558/en`
    """
    if not lang_code and "." not in url_seg_issue:
        return router_legacy_pdf(url_seg, url_seg_issue, url_seg_article)

    issue = controllers.get_issue_by_url_seg(url_seg, url_seg_issue)
    if not issue:
        abort(404, _("Issue não encontrado"))

    article = controllers.get_article_by_issue_article_seg(issue.iid, url_seg_article)
    if not article:
        abort(404, _("Artigo não encontrado"))

    req_params = {
        "url_seg": article.journal.url_segment,
        "article_pid_v3": article.aid,
        "format": "pdf",
    }
    if lang_code:
        req_params["lang"] = lang_code

    return redirect(url_for("main.article_detail_v3", **req_params), code=301)


@main.route("/pdf/<string:journal_acron>/<string:issue_info>/<string:pdf_filename>.pdf")
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def router_legacy_pdf(journal_acron, issue_info, pdf_filename):
    pdf_filename = "%s.pdf" % pdf_filename

    journal = controllers.get_journal_by_url_seg(journal_acron)

    if not journal:
        abort(
            404,
            _(
                "Este PDF não existe em %s. Consulte %s"
                % (
                    current_app.config.get("OPAC_SERVER_NAME"),
                    current_app.config.get("URL_SEARCH"),
                )
            ),
        )

    article = controllers.get_article_by_pdf_filename(
        journal_acron, issue_info, pdf_filename
    )

    # Se não tem pdf do artigo
    # Verifica se tem material suplementar
    if not article:
        article = controllers.get_article_by_suppl_material_filename(
            journal_acron, issue_info, pdf_filename
        )

    if not article:
        abort(404, _("PDF do artigo não foi encontrado"))

    return redirect(
        url_for(
            "main.article_detail_v3",
            url_seg=article.journal.url_segment,
            article_pid_v3=article.aid,
            format="pdf",
            lang=article._pdf_lang if hasattr(article, "_pdf_lang") else None,
        ),
        code=301,
    )


@main.route("/cgi-bin/fbpe/<string:text_or_abstract>/")
@cache.cached(key_prefix=cache_key_with_lang_with_qs)
def router_legacy_article(text_or_abstract):
    pid = request.args.get("pid", None)
    lng = request.args.get("lng", None)
    if not (text_or_abstract in ["fbtext", "fbabs"] and pid):
        # se tem pid
        abort(400, _("Requsição inválida ao tentar acessar o artigo com pid: %s" % pid))

    article = controllers.get_article_by_pid_v1(pid)
    if not article:
        abort(404, _("Artigo não encontrado"))

    return redirect(
        url_for(
            "main.article_detail_v3",
            url_seg=article.journal.url_segment,
            article_pid_v3=article.aid,
        ),
        code=301,
    )


@main.route("/citation/<string:article_id>/")
def article_cite_csl(article_id):
    """
    Given the ``article_id`` and return the citation to the same article with many styles.

    article_id: pid | aid.
    """

    style = request.args.get("style", "apa", type=str)
    csl = request.args.get("csl", False, type=bool)

    article = controllers.get_article_by_aid(
        article_id
    ) or controllers.get_article_by_pid(article_id)

    if article is None:
        abort(404, _("Artigo não encontrado"))

    if csl:
        return jsonify(
            article.csl_json(site_domain=current_app.config.get("OPAC_BASE_URI"))
        )

    citation = utils.render_citation(
        article.csl_json(site_domain=current_app.config.get("OPAC_BASE_URI")),
        style=style,
    )

    return citation[0] if citation else ""


@main.route("/citation/list")
def article_cite_csl_list():
    """
    Obtém a lista de CSL e retorna um formato esperado.

    Exemplo de uso dessa view function: /j/a/c/csl/list?q=ama

    Formato do retorno:

        {
            "results": [
                {
                "id": "american-marketing-association",
                "text": "American Marketing Association"
                },
                {
                "id": "american-medical-association",
                "text": "American Medical Association"
                },
                {
                "id": "american-medical-association-alphabetical",
                "text": "American Medical Association (sorted alphabetically)"
                },
                {
                "id": "american-medical-association-no-et-al",
                "text": "American Medical Association (no \"et al.\")"
                },
                {
                "id": "american-medical-association-no-url",
                "text": "American Medical Association (no URL)"
                }
            ]
        }
    """
    q = request.args.get("q", None)

    result = {"results": []}

    if q:
        q = q.lower()

        csls_json = json.loads(open(current_app.config.get("COMMON_STYLE_LIST")).read())

        for csl in csls_json.get("data"):
            title_terms = csl.get("attributes").get("title", "").lower().split(" ")

            short_title_terms = (
                csl.get("attributes").get("short_title").lower().split(" ")
                if csl.get("attributes").get("short_title")
                else []
            )
            short_title_terms += (
                csl.get("attributes").get("short_title").lower().split(" ")
                if csl.get("attributes").get("short_title")
                else []
            )

            if q in title_terms or q in short_title_terms:
                result.get("results").append(
                    {"id": csl.get("id"), "text": csl.get("attributes").get("title")}
                )

    return jsonify(result)


@main.route("/citation/export/<string:article_id>/")
def article_cite_export_format(article_id):
    """
    Given the ``article_id`` and return export citation for ["ris", "bib"]|current_app.config.get('CITATION_EXPORT_FORMAT') formats.

    Exemplo de uso dessa view function: /citation/export/<id>?format=ris

    article_id: pid | aid.
    """

    format = request.args.get("format", "ris", type=str)

    formats = current_app.config.get("CITATION_EXPORT_FORMATS")

    if not format in formats.keys():
        abort(404, _("Formato de exportação não suportado."))

    article = controllers.get_article_by_aid(
        article_id
    ) or controllers.get_article_by_pid(article_id)

    if article is None:
        abort(404, _("Artigo não encontrado."))

    csl_json = article.csl_json(site_domain=current_app.config.get("OPAC_BASE_URI"))

    if format == "bib":
        ex_citation = utils.render_citation(csl_json, style="bibtex")

    if format == "ris":
        ex_citation = render_template(
            "article/export/citation/ris", **{"csl_json": csl_json[0]}
        )

    response = Response(ex_citation, mimetype="application/octet-stream")

    response.headers["Content-Disposition"] = "attachment; filename=%s.%s" % (
        article_id,
        format,
    )

    return response


# ###############################E-mail share##################################


@main.route("/email_share_ajax/", methods=["POST"])
def email_share_ajax():
    if not request.headers.get("X-Requested-With"):
        abort(400, _("Requisição inválida."))

    form = forms.EmailShareForm(request.form)

    if form.validate():
        recipients = [
            email.strip()
            for email in form.data["recipients"].split(";")
            if email.strip() != ""
        ]

        sent, message = controllers.send_email_share(
            form.data["your_email"],
            recipients,
            form.data["share_url"],
            form.data["subject"],
            form.data["comment"],
        )

        return jsonify(
            {
                "sent": sent,
                "message": str(message),
                "fields": [key for key in form.data.keys()],
            }
        )

    else:
        return jsonify(
            {
                "sent": False,
                "message": form.errors,
                "fields": [key for key in form.data.keys()],
            }
        )


@main.route("/form_mail/", methods=["GET"])
def email_form():
    context = {"url": request.args.get("url")}
    return render_template("email/email_form.html", **context)


@main.route("/email_error_ajax/", methods=["POST"])
def email_error_ajax():
    if not request.headers.get("X-Requested-With"):
        abort(400, _("Requisição inválida."))

    form = forms.ErrorForm(request.form)

    if form.validate():
        recipients = [
            email.strip()
            for email in current_app.config.get("EMAIL_ACCOUNTS_RECEIVE_ERRORS")
            if email.strip() != ""
        ]

        sent, message = controllers.send_email_error(
            form.data["name"],
            form.data["your_email"],
            recipients,
            form.data["url"],
            form.data["error_type"],
            form.data["message"],
            form.data["page_title"],
        )

        return jsonify(
            {
                "sent": sent,
                "message": str(message),
                "fields": [key for key in form.data.keys()],
            }
        )

    else:
        return jsonify(
            {
                "sent": False,
                "message": form.errors,
                "fields": [key for key in form.data.keys()],
            }
        )


@main.route("/error_mail/", methods=["GET"])
def error_form():
    context = {"url": request.args.get("url")}
    return render_template("includes/error_form.html", **context)


# ###############################Others########################################


@main.route("/media/<path:filename>/", methods=["GET"])
@cache.cached(key_prefix=cache_key_with_lang)
def download_file_by_filename(filename):
    media_root = current_app.config["MEDIA_ROOT"]
    return send_from_directory(media_root, filename)


@main.route("/img/scielo.gif", methods=["GET"])
def full_text_image():
    return send_from_directory("static", "img/full_text_scielo_img.gif")


@main.route("/robots.txt", methods=["GET"])
def get_robots_txt_file():
    return send_from_directory("static", "robots.txt")


@main.route("/revistas/<path:journal_seg>/<string:page>.htm", methods=["GET"])
def router_legacy_info_pages(journal_seg, page):
    """
    Essa view function realiza o redirecionamento das URLs antigas para as novas URLs.

    Mantém um dicionário como uma tabela relacionamento entre o nome das páginas que pode ser:

       Página      âncora

    [iaboutj.htm, eaboutj.htm, paboutj.htm] -> #about
    [iedboard.htm, eedboard.htm, pedboard.htm] -> #editors
    [iinstruc.htm einstruc.htm, pinstruc.htm]-> #instructions
    isubscrp.htm -> Sem âncora
    """

    page_anchor = {
        "iaboutj": "#about",
        "eaboutj": "#about",
        "paboutj": "#about",
        "eedboard": "#editors",
        "iedboard": "#editors",
        "pedboard": "#editors",
        "iinstruc": "#instructions",
        "pinstruc": "#instructions",
        "einstruc": "#instructions",
    }
    return redirect(
        "%s%s"
        % (
            url_for("main.about_journal", url_seg=journal_seg),
            page_anchor.get(page, ""),
        ),
        code=301,
    )


@main.route("/api/v1/counter_dict", methods=["GET"])
def router_counter_dicts():
    """
    Essa view function retorna um dicionário, em formato JSON, que mapeia PIDs a insumos
    necessários para o funcionamento das aplicações Matomo & COUNTER & SUSHI.
    """
    end_date = request.args.get("end_date", "", type=str)
    try:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        end_date = datetime.now()
    begin_date = end_date - timedelta(days=30)

    page = request.args.get("page", type=int)
    if not page:
        page = 1

    limit = request.args.get("limit", type=int)
    if not limit or limit > 100 or limit < 0:
        limit = 100

    results = {
        "dictionary_date": end_date,
        "end_date": end_date.strftime("%Y-%m-%d %H-%M-%S"),
        "begin_date": begin_date.strftime("%Y-%m-%d %H-%M-%S"),
        "documents": {},
        "collection": current_app.config["OPAC_COLLECTION"],
    }

    articles = controllers.get_articles_by_date_range(begin_date, end_date, page, limit)
    for a in articles.items:
        results["documents"].update(get_article_counter_data(a))

    results["total"] = articles.total
    results["pages"] = articles.pages
    results["limit"] = articles.per_page
    results["page"] = articles.page

    return jsonify(results)


def get_article_counter_data(article):
    return {
        article.aid: {
            "journal_acronym": article.journal.acronym,
            "pid": article.pid if article.pid else "",
            "aop_pid": article.aop_pid if article.aop_pid else "",
            "pid_v1": article.scielo_pids.get("v1", ""),
            "pid_v2": article.scielo_pids.get("v2", ""),
            "pid_v3": article.scielo_pids.get("v3", ""),
            "publication_date": article.publication_date,
            "default_language": article.original_language,
            "create": article.created,
            "update": article.updated,
        }
    }


@main.route("/cgi-bin/wxis.exe/iah/")
def author_production():
    # http://www.scielo.br/cgi-bin/wxis.exe/iah/
    # ?IsisScript=iah/iah.xis&base=article%5Edlibrary&format=iso.pft&
    # lang=p&nextAction=lnk&
    # indexSearch=AU&exprSearch=MEIERHOFFER,+LILIAN+KOZSLOWSKI
    # ->
    # //search.scielo.org/?lang=pt&q=au:MEIERHOFFER,+LILIAN+KOZSLOWSKI

    search_url = current_app.config.get("URL_SEARCH")
    if not search_url:
        abort(404, "URL_SEARCH: {}".format(_("Página não encontrada")))

    qs_exprSearch = request.args.get("exprSearch", type=str) or ""
    qs_indexSearch = request.args.get("indexSearch", type=str) or ""
    qs_lang = request.args.get("lang", type=str) or ""

    _lang = IAHX_LANGS.get(qs_lang) or ""
    _lang = _lang and "lang={}".format(_lang)

    _expr = "{}{}".format(qs_indexSearch == "AU" and "au:" or "", qs_exprSearch)
    _expr = _expr and "q={}".format(_expr.replace(" ", "+"))

    _and = _lang and _expr and "&" or ""
    _question_mark = (_lang or _expr) and "?" or ""

    if search_url.startswith("//"):
        protocol = "https:"
    elif search_url.startswith("http"):
        protocol = ""
    else:
        protocol = "https://"

    url = "{}{}{}{}{}{}".format(
        protocol, search_url, _question_mark, _lang, _and, _expr
    )
    return redirect(url, code=301)


@main.route("/scimago/query")
def scimago_ir():
    """
    Essa view function faz um `proxy` o link para o SCImago IR(Institutions Ranking)

    Link para o página do SCImago Institutions Rankings: https://www.scimagoir.com/

    É feita uma requisição para o endereço, exemplo: https://www.scimagoir.com/query.php?q=universidade%20de%20s%C3%A3o%20paulo.

    Obtemos uma lista de links e utilizamos o priemiro link.

    Exemplo de retorno do link: https://www.scimagoir.com/query.php?q=

        <a href='institution.php?idp=773'>Universidade de Sao Paulo *</a>
        <a href='institution.php?idp=839'>Universidade Federal de Sao Paulo *</a>
        <a href='institution.php?idp=66628'>Hospital das Clinicas da Faculdade de Medicina da Universidade de Sao Paulo</a>
        <a href='institution.php?idp=735'>Pontificia Universidade Catolica de Sao Paulo</a>
        <a href='institution.php?idp=753'>Universidade Cidade de Sao Paulo</a>
        <a href='institution.php?idp=57556'>Hospital das Clinicas da Faculdade de Medicina de Ribeirao Preto da Universidade de Sao Paulo</a>
    """
    if not request.headers.get("X-Requested-With"):
        abort(400, _("Requisição inválida."))

    html = BeautifulSoup(
        requests.get(
            "%squery.php?q=%s"
            % (current_app.config.get("SCIMAGO_URL_IR"), request.args.get("q"))
        ).content
    )

    if html.find("a"):
        return html.find("a").get("href")
    else:
        return ""
