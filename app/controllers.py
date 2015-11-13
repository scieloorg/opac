# coding: utf-8
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
from app import app
import json
from pprint import pprint

ES_HOSTS = ['127.0.0.1', ]
COLLECTION = "esp"
INDEX = 'iopac3'
connections.create_connection(hosts=ES_HOSTS)


def get_journals_by_collection_alpha(collection_acronym, page_from=0, page_size=1000):

    search = Search(index=INDEX).query(
            "nested",
            path="collections",
            query=Q("match", collections__acronym=COLLECTION)).sort('title')
    search = search[page_from:page_size]
    search_response = search.execute()

    return search_response


def get_issues_by_jid(jid, page_from=0, page_size=1000, sort=None):

    if not sort:
        sort = ["-year", "-volume", "-number"]

    search = Search(index=INDEX).query(
                    "match",
                    journal_jid=jid).sort(*sort)
    search = search.query("match", _type="issue")
    search = search[page_from:page_size]
    search_response = search.execute()
    if search_response.success() and search_response.hits.total > 0:
        return search_response
    else:
        return None


def get_issue_by_iid(iid):
    search = Search(index=INDEX).query("match", iid=iid)
    search = search.query("match", _type="issue")
    search_response = search.execute()

    if search_response.success() and search_response.hits.total > 0:
        issue = search_response[0]
        return issue
    else:
        return None


def get_journal_by_jid(jid, page_from=0, page_size=1000):

    search = Search(index=INDEX).query("match", jid=jid)
    search = search[page_from:page_size]
    search_response = search.execute()

    if search_response.success() and search_response.hits.total > 0:
        journal = search_response[0]
        return journal
    else:
        return None


def get_articles_by_iid(iid, page_from=0, page_size=1000):

    search = Search(index=INDEX).query("match", issue_iid=iid)
    search = search.query("match", _type="article")

    search = search[page_from:page_size]
    search_response = search.execute()

    return search_response


def get_journals_by_collection_theme(collection_acronym, page_from=0, page_size=1000):

    search = Search(index=INDEX).query(
             "nested", path="collections", query=Q("match", collections__acronym=COLLECTION))

    search = search.query("match", _type="journal")

    search = search[page_from:page_size]
    search_response = search.execute()

    meta = {
        'total': search_response.hits.total,
    }

    # Tk no manager para sabermos as relações entre as pequenas areas e as
    # grande areas.
    large_areas = {
        'Human Sciences': {
            'Education & Educational Research': [],
            'Public, Environmental & Occupational Health': [],
        },
        'Health Sciences': {
            'Public, Environmental & Occupational Health': [],
            'Education & Educational Research': [],
            'Health Policy & Services': [],
        }
    }

    for journal in search_response:

        j = {'jid': journal.jid,
             'title': journal.title,
             'study_areas': journal.study_areas,
             'subject_categories': journal.subject_categories,
             'current_status': journal.current_status,
             'last_issue': journal.last_issue,
             'issue_count': journal.issue_count
             }

        for large_area in large_areas.keys():
            for sub_area in large_areas[large_area].keys():
                if large_area in journal.study_areas:
                    if sub_area in journal.subject_categories:
                        large_areas[large_area][sub_area].append(j)

    result = {
        'meta': meta,
        'objects': large_areas
    }

    return result


def get_journals_by_collection_indexed(collection_acronym, page_from=0, page_size=1000):

    search = Search(index=INDEX).query(
             "nested", path="collections", query=Q("match", collections__acronym=COLLECTION))

    search = search.filter("exists", field="index_at")

    search = search[page_from:page_size]
    search_response = search.execute()

    meta = {
        'total': search_response.hits.total,
    }

    index_at = {}
    for journal in search_response:

        j = {'jid': journal.jid,
             'title': journal.title,
             'current_status': journal.current_status,
             'last_issue': journal.last_issue,
             'issue_count': journal.issue_count
             }

        for index in journal['index_at']:
            index_at.setdefault(index, []).append(j)

    result = {
        'meta': meta,
        'objects': index_at
    }

    return result


def get_journals_by_collection_institution(collection_acronym, page_from=0, page_size=1000):

    search = Search(index=INDEX).query(
             "nested", path="collections", query=Q("match", collections__acronym=COLLECTION))

    search = search.filter("exists", field="sponsors")

    search = search[page_from:page_size]
    search_response = search.execute()

    meta = {
        'total': search_response.hits.total,
    }

    sponsors = {}
    for journal in search_response:

        j = {'jid': journal.jid,
             'title': journal.title,
             'current_status': journal.current_status,
             'last_issue': journal.last_issue,
             'issue_count': journal.issue_count
             }

        for sponsor in journal['sponsors']:
            sponsors.setdefault(sponsor, []).append(j)

    result = {
        'meta': meta,
        'objects': sponsors
    }

    return result


def get_article_by_aid(aid):
    search = Search(index=INDEX).query("match", aid=aid)
    search = search.query("match", _type="article")
    search_response = search.execute()

    if search_response.success() and search_response.hits.total > 0:
        article = search_response[0]
        return article
    else:
        return None
