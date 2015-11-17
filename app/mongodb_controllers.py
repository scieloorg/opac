import datetime
from mongoengine import *
from documents_definitions import DJournal


def get_journal_by_jid(jid, page_from=0, page_size=1000):

    # search = Search(index=INDEX).query("match", jid=jid)
    # search = search[page_from:page_size]
    # search_response = search.execute()

    # if search_response.success() and search_response.hits.total > 0:
    #     journal = search_response[0]
    #     return journal
    # else:
    #     return None
    return DJournal.objects(jid=jid).first()
