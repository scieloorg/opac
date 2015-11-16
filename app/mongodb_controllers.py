from mongoengine import Document, StringField, ReferenceField, DateTimeField
import datetime


class Page(Document):
    title = StringField(max_length=200, required=True)
    date_modified = DateTimeField(default=datetime.datetime.now)


def create_dummy_pages():
    for i in xrange(1, 10):
        page = Page(title='foo %s' % i)
        page.save()


def get_all_pages():
    return [page for page in Page.objects]
