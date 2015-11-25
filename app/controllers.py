# coding: utf-8

import datetime

from mongoengine import *

from opac_schema.v1.models import Journal, Issue, Article

COLLECTION = "spa"


def get_journals_by_collection_alpha(collection_acronym, page_from=0, page_size=1000):
    return Journal.objects(collections__acronym=COLLECTION).order_by('title')


def get_journal_by_jid(jid):
    return Journal.objects(jid=jid).first()


def get_issues_by_jid(jid, page_from=0, page_size=1000, sort=None):
    if not sort:
        sort = ["-year", "-volume", "-number"]
    return Issue.objects(journal_jid=jid).order_by(*sort)[page_from:page_from + page_size]


def get_issue_by_iid(iid):
    return Issue.objects(iid=iid).first()


def get_article_by_aid(aid):
    return Article.objects(aid=aid).first()


def get_articles_by_iid(iid, page_from=0, page_size=1000):
    return Article.objects(issue_iid=iid)
