import datetime
import feedparser

from webapp import controllers
from flask import url_for


def get_item_date(item):
    if 'published_parsed' in list(item.keys()):
        return datetime.datetime(*item.published_parsed[:7])
    else:
        return datetime.datetime.now()


def get_items_from_feed(url):
    feed = feedparser.parse(url)

    if feed.bozo == 1:
        msg = 'Não é possível parsear o feed (%s)' % url
        return False, msg

    return feed['items'], False


def news_import(url, language):
    entries, error_msg = get_items_from_feed(url)

    if not entries:
        return False, error_msg

    for item in entries:
        news_data = dict(url=item.link,
                         image_url=url_for('static',
                                           filename='img/fallback_image.png',
                                           _external=True),
                         publication_date=get_item_date(item),
                         title=item.title[:256],
                         description=item.summary,
                         language=language)
        controllers.create_news_record(news_data)

    return True, False


def import_all_press_releases_posts(url, language):
    entries, error_msg = get_items_from_feed(url)

    if not entries:
        return False, error_msg

    for item in entries:
        journals = controllers.get_journals()

        for tag in item['tags']:
            if not tag.term.isupper():
                continue

            journal = journals.filter(acronym=tag.term)
            if len(journal) == 0:
                continue

            pr_data = dict(url=item.link,
                           jornal=journal,
                           image_url=url_for('static',
                                             filename='img/fallback_image.png',
                                             _external=True),
                           publication_date=get_item_date(item),
                           title=item.title[:256],
                           description=item.summary,
                           language=language)
            controllers.create_press_release_record(pr_data)

    return True, False


def import_all_press_releases_posts_by_category(url, language):
    journals = controllers.get_journals()

    for journal in journals:
        dynamic_url = url.format(language, journal.acronym)   # warning: Concatenations on this url see the default.py
        entries = get_items_from_feed(dynamic_url)

        for item in entries[0]:
            pr_data = dict(url=item.link,
                           journal=journal,
                           publication_date=get_item_date(item),
                           title=item.title[:256],
                           content=item.summary,
                           language=language)
            controllers.create_press_release_record(pr_data)

    return True, False
