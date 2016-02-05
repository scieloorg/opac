# coding: utf-8

from uuid import uuid4

from opac_schema.v1 import models


def makeOneJournal(attrib=None):
    """
    Retorna um objeto ``Journal`` com os atributos obrigatórios:
    ``_id``, ``jid``, ``is_public``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """
    if not attrib:
        attrib = {}

    if '_id' not in attrib:
        _id = str(uuid4().hex)
    else:
        _id = attrib['_id']

    acron = "journal-%s" % _id
    journal = {'_id': _id, 'jid': _id, 'is_public': True, 'acronym': acron}

    if attrib and isinstance(attrib, dict):
        journal.update(attrib)

    return models.Journal(**journal).save()


def makeAnyJournal(items=3):
    """
    Retorna uma lista de objetos ``Journal`` com atributos ``jid``,
    ``is_public`` e ``acronym`` limitando a quantidade pelo param ``items``.
    """
    journals = []

    for item in range(items):

        journal = makeOneJournal()

        journals.append(journal)

    return journals


def makeOneIssue(attrib=None):
    """
    Retorna um objeto ``Issue`` com os atributos obrigatórios:
    ``_id``, ``jid``, ``is_public`` e ``journal_jid``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """

    journal = makeOneJournal()

    if not attrib:
        attrib = {}

    if '_id' not in attrib:
        _id = str(uuid4().hex)
    else:
        _id = attrib['_id']

    issue = {'_id': _id, 'iid': _id, 'is_public': True,
             'journal': journal.id}

    if attrib and isinstance(attrib, dict):
        issue.update(attrib)

    return models.Issue(**issue).save()


def makeAnyIssue(journal=None, items=3):
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

        issue = makeOneIssue()

        issues.append(issue)

    return issues


def makeOneArticle(attrib=None):
    """
    Retorna um objeto ``Article`` com os atributos obrigatórios:
    ``_id``, ``aid``, ``is_public``.
    Atualiza o objeto de retorno com os valores do param ``attrib``.
    """

    issue = makeOneIssue()

    if not attrib:
        attrib = {}

    if '_id' not in attrib:
        _id = str(uuid4().hex)
    else:
        _id = attrib['_id']

    title = "article-%s" % _id
    article = {'_id': _id, 'aid': _id, 'is_public': True,
               'issue': issue.id, 'title': title}

    if attrib and isinstance(attrib, dict):
        article.update(attrib)

    return models.Article(**article).save()


def makeAnyArticle(issue=None, items=3):
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

        article = makeOneArticle()

        articles.append(article)

    return articles
