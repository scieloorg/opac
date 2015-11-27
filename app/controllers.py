# coding: utf-8

import datetime

from mongoengine import *

from opac_schema.v1.models import Journal, Issue, Article

from . import app

COLLECTION = app.config['OPAC_COLLECTION']


def get_journals_alpha():
    return Journal.objects(collections__acronym=COLLECTION).order_by('title')


def get_journal_by_jid(jid):
    return Journal.objects(jid=jid).first()


def get_issues_by_jid(jid, sort=None):
    if not sort:
        sort = ["-year", "-volume", "-number"]
    return Issue.objects(journal_jid=jid).order_by(*sort)


def get_issue_by_iid(iid):
    return Issue.objects(iid=iid).first()


def get_article_by_aid(aid):
    return Article.objects(aid=aid).first()


def get_articles_by_iid(iid):
    return Article.objects(issue_iid=iid)
