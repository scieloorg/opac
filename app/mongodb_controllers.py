import datetime
from mongoengine import *
from documents_definitions import DJournal, DIssue


def get_journal_by_jid(jid):

    return DJournal.objects(jid=jid).first()


def get_issues_by_jid(jid, page_from=0, page_size=1000, sort=None):

    if not sort:
        sort = ["-year", "-volume", "-number"]

    return DIssue.objects(journal_jid=jid).order_by(*sort)[page_from:page_from + page_size]


def get_issue_by_iid(iid):

    return DIssue.objects(iid=iid).first()
