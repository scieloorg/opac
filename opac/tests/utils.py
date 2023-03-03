# coding: utf-8
import datetime
import random
from uuid import uuid4

from flask import current_app
from opac_schema.v1 import models
from slugify import slugify


def makeOneCollection(attrib=None):  # noqa
    """
    Retorna um objeto ``Collection`` com os atributos obrigatórios:
    ``_id``, ``acronym``, ``name``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """
    attrib = attrib or {}
    default_id = attrib.get("_id", str(uuid4().hex))
    config_acronym = current_app.config["OPAC_COLLECTION"]

    name = attrib.get("name", "collection of %s" % config_acronym)
    acronym = attrib.get("acronym", config_acronym)

    metrics = {
        "total_journal": attrib.get("total_journal", 0),
        "total_issue": attrib.get("total_issue", 0),
        "total_article": attrib.get("total_article", 0),
        "total_citation": attrib.get("total_citation", 0),
    }

    collection = {
        "_id": default_id,
        "name": name,
        "acronym": acronym,
        "metrics": metrics,
        "sponsors": attrib.get("sponsors", None),
    }
    for k, v in attrib.items():
        if k not in list(collection.keys()):
            collection[k] = v
    return models.Collection(**collection).save()


def makeOneSponsor(attrib=None):  # noqa
    """
    Retorna um objeto ``Sponsor`` com os atributos obrigatórios:
    ``_id``, ``acronym``, ``name``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """
    attrib = attrib or {}
    default_id = attrib.get("_id", str(uuid4().hex))
    name = attrib.get("name", "sponsor (%s)" % default_id)

    collection = {
        "_id": default_id,
        "order": attrib.get("order", 0),
        "name": name,
        "url": attrib.get("url", None),
        "logo_url": attrib.get("logo_url", None),
    }
    return models.Sponsor(**collection).save()


def makeOneJournal(attrib=None):  # noqa
    """
    Retorna um objeto ``Journal`` com os atributos obrigatórios:
    ``_id``, ``jid``, ``is_public``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """
    attrib = attrib or {}
    default_id = attrib.get("_id", str(uuid4().hex))
    default_title = "journal-%s" % default_id
    default_title_iso = default_title[:6]

    if "social_networks" in list(attrib.keys()):
        social_networks = []
        for sn in attrib["social_networks"]:
            social_account = models.SocialNetwork(
                account=sn["account"], network=sn["network"]
            )
            social_networks.append(social_account)
        attrib["social_networks"] = social_networks

    journal = {
        "_id": default_id,
        "jid": attrib.get("jid", default_id),
        "is_public": attrib.get("is_public", True),
        "title": attrib.get("title", default_title),
        "title_iso": attrib.get("title_iso", default_title_iso),
        "short_title": attrib.get("short_title", "Jounal Ex."),
        "created": attrib.get("created", datetime.datetime.now()),
        "updated": attrib.get("updated", datetime.datetime.now()),
        "acronym": attrib.get("acronym", "journal_acron"),
        "mission": attrib.get(
            "mission",
            [
                {
                    "language": "pt",
                    "description": "Esse periódico tem com objetivo xpto",
                },
                {
                    "language": "es",
                    "description": "Esta revista tiene como objetivo xpto",
                },
                {"language": "en", "description": "This journal is aiming xpto"},
            ],
        ),
    }
    if not journal.get("is_public") and not journal.get("unpublish_reason"):
        journal["unpublish_reason"] = "<unpublish_reason>"
    journal.update(attrib)
    return models.Journal(**journal).save()


def makeAnyJournal(items=3, attrib=None):  # noqa
    """
    Retorna uma lista de objetos ``Journal`` com atributos ``jid``,
    ``is_public`` e ``acronym`` limitando a quantidade pelo param ``items``.
    Param attrib para adicionar atributo aos objecto do tipo Journal
    """
    journals = []

    for _ in range(items):
        journal = makeOneJournal(attrib)

        journals.append(journal)

    return journals


def makeOnePage(attrib=None):  # noqa
    """
    Retorna um objeto ``Page`` com os atributos obrigatórios:
    ``_id``, ``jid``, ``is_public``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """
    attrib = attrib or {}
    default_id = attrib.get("_id", str(uuid4().hex))
    default_name = "page-%s" % default_id
    texts = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        + " Ut cursus porttitor suscipit. "
        + "Suspendisse ut dolor volutpat, "
        + "tempor eros nec, tincidunt dui. Integer id ornare lectus, "
        + "sit amet consectetur leo. Mauris massa massa, "
        + "ut, euismod aliquet erat. Cras id blandit magna, et porttitor"
        + " purus. Vestibulum rhoncus euismod purus at ultrices. "
    )
    texts = texts.split()
    times = random.choice(range(10, len(texts)))

    page = {
        "_id": default_id,
        "name": attrib.get("name", default_name),
        "slug_name": slugify(attrib.get("name", default_name)),
        "journal": attrib.get("journal", ""),
        "is_draft": attrib.get("is_draft", False),
        "content": " ".join([random.choice(texts) for n in range(0, times)]),
        "description": "Description {}".format(default_name),
        "language": attrib.get("language", "pt_BR"),
        "created_at": attrib.get("created", datetime.datetime.now()),
        "updated_at": attrib.get("updated", datetime.datetime.now()),
    }
    page.update(attrib)
    return models.Pages(**page).save()


def makeAnyPage(items=3, attrib=None):  # noqa
    """
    Retorna uma lista de objetos ``Pages`` com atributos ``jid``,
    ``is_public`` e ``acronym`` limitando a quantidade pelo param ``items``.
    Param attrib para adicionar atributo aos objecto do tipo Pages
    """
    pages = []

    for _ in range(items):
        page = makeOnePage(attrib)

        pages.append(page)

    return pages


def makeOneIssue(attrib=None):  # noqa
    """
    Retorna um objeto ``Issue`` com os atributos obrigatórios:
    ``_id``, ``jid``, ``is_public`` e ``journal_jid``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """

    attrib = attrib or {}
    default_id = attrib.get("_id", str(uuid4().hex))
    default_volume = attrib.get("volume", "1")  # improve para evitar dups
    default_number = attrib.get("number", "1")  # improve para evitar dups
    default_type = attrib.get("type", "regular")
    default_pid = attrib.get("pid", "0000-000000000000")
    default_order = attrib.get("order", attrib.get("order", "1"))
    default_year = attrib.get("year", datetime.datetime.now().year)
    default_label = attrib.get("label", "%s (%s)" % (default_volume, default_number))
    default_suppl_text = attrib.get("suppl_text", "X")
    journal = attrib.get("journal", None)

    if not journal:
        journal = makeOneJournal()
    elif isinstance(journal, str) or isinstance(journal, str):
        # o valor de: journal é o Id do journal
        try:
            journal = models.Journal.objects.get(_id=journal)
        except models.Journal.DoesNotExist:
            journal = makeOneJournal({"_id": journal})
    elif isinstance(journal, models.Journal):
        pass
    else:
        raise ValueError("WTF is journal?")

    issue = {
        "_id": default_id,
        "iid": default_id,
        "volume": default_volume,
        "number": default_number,
        "type": default_type,
        "order": default_order,
        "year": default_year,
        "label": default_label,
        "suppl_text": default_suppl_text,
        "pid": default_pid,
        "is_public": attrib.get("is_public", True),
        "created": attrib.get("created", datetime.datetime.now()),
        "updated": attrib.get("updated", datetime.datetime.now()),
        "journal": journal.id,
    }

    for k, v in attrib.items():
        if k not in list(issue.keys()):
            issue[k] = v

    return models.Issue(**issue).save()


def makeAnyIssue(journal=None, items=3, attrib=None):  # noqa
    """
    Retorna uma lista de objetos ``Issue`` com atributos ``iid``,
    ``journal`` limitando a quantidade pelo param ``items``e o param journal
    permiti definir um objeto ``Journal`` para o issue ou será criado
    automáticamente.
    """
    issues = []

    if not journal:
        journal = makeOneJournal()

    for _ in range(items):
        issue = makeOneIssue(attrib)

        issues.append(issue)

    return issues


def makeOneArticle(attrib=None):  # noqa
    """
    Retorna um objeto ``Article`` com os atributos obrigatórios:
    ``_id``, ``aid``, ``is_public``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """

    attrib = attrib or {}
    default_id = attrib.get("_id", str(uuid4().hex))
    default_pid = attrib.get("pid", "0000-00000000000000000")
    default_title = "article-%s" % default_id
    default_domain_key = "article-domain_key-%s" % default_id
    issue = attrib.get("issue", None)
    journal = attrib.get("journal", None)

    if not journal:
        journal = makeOneJournal()
    elif isinstance(journal, str) or isinstance(journal, str):
        # o valor de: journal é o Id do journal
        try:
            journal = models.Journal.objects.get(_id=journal)
        except models.Journal.DoesNotExist:
            journal = makeOneJournal({"_id": journal})
    elif isinstance(journal, models.Journal):
        pass
    else:
        raise ValueError("WTF is journal?")

    if not issue:
        issue = makeOneIssue({"journal": journal})
    elif isinstance(issue, str) or isinstance(issue, str):
        # o valor de: issue é o Id do issue
        try:
            issue = models.Issue.objects.get(_id=issue, journal=journal.id)
        except models.Issue.DoesNotExist:
            issue = makeOneIssue({"_id": issue, "journal": journal.id})
    elif isinstance(issue, models.Issue):
        pass
    else:
        raise ValueError("WTF is issue?")

    article = {
        "_id": default_id,
        "aid": default_id,
        "title": attrib.get("title", default_title),
        "domain_key": attrib.get("domain_key", default_domain_key),
        "is_aop": attrib.get("is_aop", False),
        "is_public": attrib.get("is_public", True),
        "created": attrib.get("created", datetime.datetime.now()),
        "updated": attrib.get("updated", datetime.datetime.now()),
        "issue": issue.id,
        "journal": journal.id,
        "pid": default_pid,
        "original_language": attrib.get("original_language", "pt"),
        "fpage": attrib.get("fpage", "15"),
        "lpage": attrib.get("lpage", "16"),
        "translated_titles": attrib.get("translated_titles", []),
        "languages": attrib.get(
            "languages",
            [
                "pt",
            ],
        ),
        "publication_date": "2000",
    }
    article.update(attrib)

    return models.Article(**article).save()


def makeAnyArticle(issue=None, items=3, attrib=None):  # noqa
    """
    Retorna uma lista de objetos ``Article`` com atributos ``aid``,
    ``issue`` limitando a quantidade pelo param ``items`` e o param issue
    permiti definir um objeto ``Issue`` para o artcile ou será c riado
    automáticamente.
    """
    articles = []

    if not issue:
        issue = makeOneIssue()

    for _ in range(items):
        article = makeOneArticle(attrib)

        articles.append(article)

    return articles


def getLastIssue(attrib=None):  # noqa
    """
    Retorna um objeto ``LastIssue`` com os atributos obrigatórios:
    ``_id``, ``jid``, ``is_public`` e ``journal_jid``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """
    attrib = attrib or {}
    attributes = (
        ("volume", "100"),
        ("number", "100"),
        ("year", 2030),
        ("label", "label"),
        ("type", "regular"),
        ("suppl_text", None),
        ("start_month", 1),
        ("end_month", 1),
        ("sections", None),
        ("cover_url", ""),
        ("iid", "ID"),
    )
    last_issue = {}
    for k, val in attributes:
        last_issue[k] = attrib.get(k) or val
    last_issue["url_segment"] = "{}.{}{}{}".format(
        last_issue.get("year"),
        "v" + last_issue.get("volume") if last_issue.get("volume") else "",
        "n" + last_issue.get("number") if last_issue.get("number") else "",
        last_issue.get("suppl_text") or "",
    )
    return models.LastIssue(**last_issue)
