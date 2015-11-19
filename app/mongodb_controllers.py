import datetime
from mongoengine import *
from documents_definitions import DJournal, DIssue, DArticle

COLLECTION = "spa"


def get_journals_by_collection_alpha(collection_acronym, page_from=0, page_size=1000):
    return DJournal.objects(collections__acronym=COLLECTION).order_by('title')


def get_journal_by_jid(jid):
    return DJournal.objects(jid=jid).first()


def get_issues_by_jid(jid, page_from=0, page_size=1000, sort=None):
    if not sort:
        sort = ["-year", "-volume", "-number"]
    return DIssue.objects(journal_jid=jid).order_by(*sort)[page_from:page_from + page_size]


def get_issue_by_iid(iid):
    return DIssue.objects(iid=iid).first()


def get_article_by_aid(aid):
    return DArticle.objects(aid=aid).first()


def get_articles_by_iid(iid, page_from=0, page_size=1000):
    return DArticle.objects(issue_iid=iid)
