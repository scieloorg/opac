# coding: utf-8

import datetime

from opac_schema.v1.models import Journal, Issue, Article
from flask import current_app


def get_journals_alpha():
    COLLECTION = current_app.config.get('OPAC_COLLECTION')
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


# -------- SLQALCHEMY --------
def get_user(email):
    import models as sql_models
    from . import dbsql
    return dbsql.session.query(sql_models.User).filter_by(email=email).first()


def get_user_by_id(id):
    import models as sql_models
    from . import dbsql
    return dbsql.session.query(sql_models.User).get(id)
