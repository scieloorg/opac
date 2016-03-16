# coding: utf-8

from base import BaseTestCase
from flask.ext.admin.contrib.mongoengine.tools import parse_like_term
from flask_babelex import lazy_gettext as __
from uuid import uuid4
from app.admin.custom_filters import (
    get_flt, CustomFilterConverter, CustomFilterLike, CustomFilterNotLike, CustomFilterEqual,
    CustomFilterNotEqual, CustomFilterEmpty, CustomFilterInList, CustomFilterNotInList)
from mongoengine.queryset import Q
from opac_schema.v1.models import Journal, Issue, Article
from tests.utils import makeOneJournal, makeOneIssue, makeOneArticle


class CustomFiltersTestCase(BaseTestCase):

    def test_flt_reference_journal(self):

        journal_fields = {'title': 'title-%s' % str(uuid4().hex),
                         'title_iso': 'title_iso-%s' % str(uuid4().hex),
                         'short_title': 'short_title-%s' % str(uuid4().hex),
                         'acronym': 'acronym-%s' % str(uuid4().hex),
                         'print_issn': 'print_issn-%s' % str(uuid4().hex),
                         'eletronic_issn': 'eletronic_issn-%s' % str(uuid4().hex)}

        journal = makeOneJournal(journal_fields)
        makeOneIssue({'journal': journal})

        for field in journal_fields:
            op, term = parse_like_term(journal[field])
            result = get_flt(Issue.journal, term, op)

            journals = Journal.objects.filter(Q(**{'%s__%s'% (field, op): term}))
            expected = Q(**{'journal__in': journals})

            self.assertIn('journal__in', result.query)
            self.assertItemsEqual(expected.query['journal__in'], result.query['journal__in'])

    def test_flt_search_reference_issue(self):

        journal = makeOneJournal()
        issue = makeOneIssue({'journal': journal})
        makeOneArticle({'journal': journal, 'issue': issue})

        op, term = parse_like_term(issue.label)
        result = get_flt(Article.issue, term, op)

        issues = Issue.objects.filter(Q(**{'label__%s'% op: term}))
        expected = Q(**{'issue__in': issues})

        self.assertIn('issue__in', result.query)
        self.assertItemsEqual(expected.query['issue__in'], result.query['issue__in'])

    def test_flt_embedded_use_licenses(self):

        op, term = parse_like_term('CC-%s' % str(uuid4().hex))
        expected = Q(**{'use_licenses__license_code__%s' % op: term})
        expected |= Q(**{'use_licenses__reference_url__%s' % op: term})
        expected |= Q(**{'use_licenses__disclaimer__%s' % op: term})
        expected_children = [i.query for i in expected.children]

        result = get_flt(Journal.use_licenses, term, op)
        self.assertEqual(expected.operation, result.operation)
        self.assertEqual(expected_children, [i.query for i in result.children])

    def test_flt_list_field(self):

        op, term = parse_like_term('title-%s' % str(uuid4().hex))
        result = get_flt(Journal.title, term, op)

    def test_flt_string_field(self):
        op, term = parse_like_term('index-%s' % str(uuid4().hex))

        result = get_flt(Journal.index_at, term, op)

        expected = Q(**{'%s__%s' % (Journal.index_at.name, op): term})

        self.assertEqual(expected.query, result.query)

    def test_filters_reference_field(self):

        filter_converter = CustomFilterConverter()
        filtes_reference_field = (CustomFilterLike, CustomFilterNotLike, CustomFilterEqual,
                         CustomFilterNotEqual, CustomFilterInList, CustomFilterNotInList)

        result = filter_converter.convert('ReferenceField', Issue.journal, 'journal')
        expected = [f(Issue.journal, 'journal') for f in filtes_reference_field]

        self.assertItemsEqual([vars(i) for i in expected], [vars(i) for i in result])

    def test_filters_embedded_field(self):

        filter_converter = CustomFilterConverter()
        filtes_embedded_field = (CustomFilterLike, CustomFilterNotLike, CustomFilterEqual,
                         CustomFilterNotEqual, CustomFilterEmpty, CustomFilterInList,
                         CustomFilterNotInList)

        result = filter_converter.convert('EmbeddedDocumentField', Journal.use_licenses, 'use_licenses')
        expected = [f(Journal.use_licenses, 'use_licenses') for f in filtes_embedded_field]

        self.assertItemsEqual([vars(i) for i in expected], [vars(i) for i in result])

    def test_filters_list_field(self):

        filter_converter = CustomFilterConverter()
        filtes_list_field = (CustomFilterLike, CustomFilterNotLike, CustomFilterEmpty)

        result = filter_converter.convert('ListField', Journal.index_at, 'index_at')
        expected = [f(Journal.index_at, 'index_at') for f in filtes_list_field]

        self.assertItemsEqual([vars(i) for i in expected], [vars(i) for i in result])


    def test_custom_filter_equal(self):

        journal_fields = {'title': 'title-%s' % str(uuid4().hex)}
        journal = makeOneJournal(journal_fields)
        makeOneIssue({'journal': journal})
        column = Issue.journal
        custom_filter = CustomFilterEqual(column=column, name=__(u'Periódico'))

        result = custom_filter.apply(Issue.objects, journal.title)

        journals = Journal.objects.filter(Q(**{'title__': journal.title}))
        expected = Issue.objects.filter(Q(**{'%s__in' % column.name: journals}))

        self.assertItemsEqual(expected, result)

    def test_custom_filter_not_equal(self):

        journal = makeOneJournal({'title': 'title-%s' % str(uuid4().hex)})
        makeOneIssue({'journal': journal})
        column = Issue.journal
        custom_filter = CustomFilterNotEqual(column=column, name=__(u'Periódico'))

        result = custom_filter.apply(Issue.objects, journal.title)

        journals = Journal.objects.filter(Q(**{'title__ne': journal.title}))
        expected = Issue.objects.filter(Q(**{'%s__in' % column.name: journals}))

        self.assertItemsEqual(expected, result)

    def test_custom_filter_like(self):

        journal = makeOneJournal({'title': 'title-%s' % str(uuid4().hex)})
        makeOneIssue({'journal': journal})
        column = Issue.journal
        custom_filter = CustomFilterLike(column=column, name=__(u'Periódico'))

        result = custom_filter.apply(Issue.objects, journal.title)

        term, data = parse_like_term(journal.title)
        journals = Journal.objects.filter(Q(**{'title__%s' % term: data}))
        expected = Issue.objects.filter(Q(**{'%s__in' % column.name: journals}))

        self.assertItemsEqual(expected, result)

    def test_custom_filter_not_like(self):

        journal = makeOneJournal({'title': 'title-%s' % str(uuid4().hex)})
        makeOneIssue({'journal': journal})
        column = Issue.journal
        custom_filter = CustomFilterNotLike(column=column, name=__(u'Periódico'))

        result = custom_filter.apply(Issue.objects, journal.title)

        term, data = parse_like_term(journal.title)
        journals = Journal.objects.filter(Q(**{'title__not__%s' % term: data}))
        expected = Issue.objects.filter(Q(**{'%s__in' % column.name: journals}))

        self.assertItemsEqual(expected, result)

    def test_custom_filter_in_list(self):

        journal = makeOneJournal({'title': 'title-%s' % str(uuid4().hex)})
        makeOneIssue({'journal': journal})
        column = Issue.journal
        custom_filter = CustomFilterInList(column=column, name=__(u'Periódico'))

        result = custom_filter.apply(Issue.objects, [journal.title])

        journals = Journal.objects.filter(Q(**{'title__in': [journal.title]}))
        expected = Issue.objects.filter(Q(**{'%s__in' % column.name: journals}))

        self.assertItemsEqual(expected, result)

    def test_custom_filter_not_in_list(self):

        journal = makeOneJournal({'title': 'title-%s' % str(uuid4().hex)})
        makeOneIssue({'journal': journal})
        column = Issue.journal
        custom_filter = CustomFilterNotInList(column=column, name=__(u'Periódico'))

        result = custom_filter.apply(Issue.objects, [journal.title])

        journals = Journal.objects.filter(Q(**{'title__nin': [journal.title]}))
        expected = Issue.objects.filter(Q(**{'%s__in' % column.name: journals}))

        self.assertItemsEqual(expected, result)
