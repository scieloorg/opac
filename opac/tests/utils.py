# coding: utf-8
import datetime
from uuid import uuid4
from flask import current_app
from opac_schema.v1 import models


def makeOneCollection(attrib=None):
    """
    Retorna um objeto ``Collection`` com os atributos obrigatórios:
    ``_id``, ``acronym``, ``name``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """
    attrib = attrib or {}
    default_id = attrib.get('_id', str(uuid4().hex))
    config_acronym = current_app.config['OPAC_COLLECTION']

    name = attrib.get('name', 'collection of %s' % config_acronym)
    license_code = attrib.get('license_code', 'CC-BY')
    acronym = attrib.get('acronym', config_acronym)

    collection = {
        '_id': default_id,
        'name': name,
        'acronym': acronym,
        'license_code': license_code,
        'logo_url': attrib.get('logo_url', None),
        'sponsors': attrib.get('sponsors', None),
    }
    for k, v in attrib.iteritems():
        if k not in collection.keys():
            collection[k] = v
    return models.Collection(**collection).save()


def makeOneSponsor(attrib=None):
    """
    Retorna um objeto ``Sponsor`` com os atributos obrigatórios:
    ``_id``, ``acronym``, ``name``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """
    attrib = attrib or {}
    default_id = attrib.get('_id', str(uuid4().hex))
    name = attrib.get('name', 'sponsor (%s)' % default_id)

    collection = {
        '_id': default_id,
        'name': name,
        'url': attrib.get('url', None),
        'logo_url': attrib.get('logo_url', None),
    }
    return models.Sponsor(**collection).save()


def makeOneJournal(attrib=None):
    """
    Retorna um objeto ``Journal`` com os atributos obrigatórios:
    ``_id``, ``jid``, ``is_public``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """
    attrib = attrib or {}
    default_id = attrib.get('_id', str(uuid4().hex))

    journal = {
        '_id': default_id,
        'jid': attrib.get('jid', default_id),
        'is_public': attrib.get('is_public', True),
        'created': attrib.get('created', datetime.datetime.now()),
        'updated': attrib.get('updated', datetime.datetime.now()),
        'acronym': attrib.get('acronym', "journal-%s" % default_id)
    }
    journal.update(attrib)
    return models.Journal(**journal).save()


def makeAnyJournal(items=3, attrib=None):
    """
    Retorna uma lista de objetos ``Journal`` com atributos ``jid``,
    ``is_public`` e ``acronym`` limitando a quantidade pelo param ``items``.
    Param attrib para adicionar atributo aos objecto do tipo Journal
    """
    journals = []

    for item in range(items):

        journal = makeOneJournal(attrib)

        journals.append(journal)

    return journals


def makeOneIssue(attrib=None):
    """
    Retorna um objeto ``Issue`` com os atributos obrigatórios:
    ``_id``, ``jid``, ``is_public`` e ``journal_jid``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """

    attrib = attrib or {}
    default_id = attrib.get('_id', str(uuid4().hex))
    default_volume = attrib.get('volume', '1')  # improve para evitar dups
    default_number = attrib.get('number', '1')  # improve para evitar dups
    default_year = attrib.get('year', datetime.datetime.now().year)
    default_label = attrib.get('label', '%s (%s)' % (default_volume, default_number))
    journal = attrib.get('journal', None)

    if not journal:
        journal = makeOneJournal()
    elif isinstance(journal, str) or isinstance(journal, unicode):
        # o valor de: journal é o Id do journal
        try:
            journal = models.Journal.objects.get(_id=journal)
        except models.Journal.DoesNotExist:
            journal = makeOneJournal({'_id': journal})
    elif isinstance(journal, models.Journal):
        pass
    else:
        raise ValueError('WTF is journal?')

    issue = {
        '_id': default_id,
        'iid': default_id,
        'volume': default_volume,
        'number': default_number,
        'year': default_year,
        'label': default_label,
        'is_public': attrib.get('is_public', True),
        'created': attrib.get('created', datetime.datetime.now()),
        'updated': attrib.get('updated', datetime.datetime.now()),
        'journal': journal.id
    }

    for k, v in attrib.iteritems():
        if k not in issue.keys():
            issue[k] = v

    return models.Issue(**issue).save()


def makeAnyIssue(journal=None, items=3, attrib=None):
    """
    Retorna uma lista de objetos ``Issue`` com atributos ``iid``,
    ``journal`` limitando a quantidade pelo param ``items``e o param journal
    permiti definir um objeto ``Journal`` para o issue ou será criado
    automáticamente.
    """
    issues = []

    if not journal:
        journal = makeOneJournal()

    for item in range(items):

        issue = makeOneIssue(attrib)

        issues.append(issue)

    return issues


def makeOneArticle(attrib=None):
    """
    Retorna um objeto ``Article`` com os atributos obrigatórios:
    ``_id``, ``aid``, ``is_public``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """

    attrib = attrib or {}
    default_id = attrib.get('_id', str(uuid4().hex))
    default_title = "article-%s" % default_id
    default_domain_key = "article-domain_key-%s" % default_id
    issue = attrib.get('issue', None)
    journal = attrib.get('journal', None)

    if not journal:
        journal = makeOneJournal()
    elif isinstance(journal, str) or isinstance(journal, unicode):
        # o valor de: journal é o Id do journal
        try:
            journal = models.Journal.objects.get(_id=journal)
        except models.Journal.DoesNotExist:
            journal = makeOneJournal({'_id': journal})
    elif isinstance(journal, models.Journal):
        pass
    else:
        raise ValueError('WTF is journal?')

    if not issue:
        issue = makeOneIssue({'journal': journal})
    elif isinstance(issue, str) or isinstance(issue, unicode):
        # o valor de: issue é o Id do issue
        try:
            issue = models.Issue.objects.get(_id=issue, journal=journal.id)
        except models.Issue.DoesNotExist:
            issue = makeOneIssue({'_id': issue, 'journal': journal.id})
    elif isinstance(issue, models.Issue):
        pass
    else:
        raise ValueError('WTF is issue?')

    article = {
        '_id': default_id,
        'aid': default_id,
        'title': attrib.get('title', default_title),
        'domain_key': attrib.get('domain_key', default_domain_key),
        'is_aop': attrib.get('is_aop', False),
        'is_public': attrib.get('is_public', True),
        'created': attrib.get('created', datetime.datetime.now()),
        'updated': attrib.get('updated', datetime.datetime.now()),
        'issue': issue.id,
        'journal': journal.id,
    }

    for k, v in attrib.iteritems():
        if k not in article.keys():
            article[k] = v

    return models.Article(**article).save()


def makeAnyArticle(issue=None, items=3, attrib=None):
    """
    Retorna uma lista de objetos ``Article`` com atributos ``aid``,
    ``issue`` limitando a quantidade pelo param ``items`` e o param issue
    permiti definir um objeto ``Issue`` para o artcile ou será criado
    automáticamente.
    """
    articles = []

    if not issue:
        issue = makeOneIssue()

    for item in range(items):

        article = makeOneArticle(attrib)

        articles.append(article)

    return articles
