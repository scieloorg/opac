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

    if not attrib:
        attrib = {}

    if '_id' not in attrib:
        _id = str(uuid4().hex)
    else:
        _id = attrib['_id']

    if 'journal' not in attrib:
        journal = makeOneJournal().id
    else:
        journal = attrib['journal']

    issue = {'_id': _id, 'iid': _id, 'is_public': True,
             'journal': journal}

    if attrib and isinstance(attrib, dict):
        issue.update(attrib)

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

    if not attrib:
        attrib = {}

    if '_id' not in attrib:
        _id = str(uuid4().hex)
    else:
        _id = attrib['_id']

    if 'issue' not in attrib and 'journal' not in attrib:
        issue = makeOneIssue()
        issue_id = issue.id
        journal_id = issue.journal
    else:
        issue_id = attrib['issue']
        journal_id = attrib['journal']

    title = "article-%s" % _id
    article = {'_id': _id, 'aid': _id, 'is_public': True,
               'journal': journal_id, 'issue': issue_id, 'title': title}

    if attrib and isinstance(attrib, dict):
        article.update(attrib)

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
