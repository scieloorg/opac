# coding: utf-8
from flask.ext.admin.contrib.mongoengine.filters import (
    FilterEqual, FilterNotEqual, FilterLike, FilterNotLike,
    FilterEmpty, FilterInList, FilterNotInList, FilterConverter)
from flask.ext.admin.contrib.mongoengine.tools import parse_like_term
from flask.ext.admin.model import filters
from mongoengine import ReferenceField, EmbeddedDocumentField, ListField, StringField
from mongoengine.queryset import Q
from opac_schema.v1.models import Journal, Issue


def get_flt(column=None, value=None, term=''):
    flt = None
    search_fields = {
        'journal': ['jid', 'title', 'title_iso', 'short_title', 'acronym', 'print_issn', 'eletronic_issn'],
        'issue': ['label'],
        'use_licenses': ['license_code']
    }

    if isinstance(column, ReferenceField):
        criteria = None
        reference_values = None
        for field in search_fields[column.name]:
            flt = {'%s__%s' % (field, term): value}
            q = Q(**flt)

            if criteria is None:
                criteria = q
            elif term in ['ne', 'not__contains', 'nin']:
                criteria &= q
            else:
                criteria |= q
        if isinstance(column.document_type_obj(), Journal):
            reference_values = Journal.objects.filter(criteria)
        elif isinstance(column.document_type_obj(), Issue):
            reference_values = Issue.objects.filter(criteria)
        flt = {'%s__in' % column.name: reference_values}

    elif isinstance(column, EmbeddedDocumentField):
        criteria = None
        for field in search_fields[column.name]:
            flt = {'%s__%s__%s' % (column.name, field, term): value}
            q = Q(**flt)

            if criteria is None:
                criteria = q
            elif term in ['ne', 'not__contains', 'nin']:
                criteria &= q
            else:
                criteria |= q
        return criteria

    elif isinstance(column, ListField) and isinstance(column.field, StringField):
        flt = {'%s__%s' % (column.name, term): value if value else []}

    else:
        flt = {'%s__%s' % (column.name, term): value}

    return Q(**flt)


class CustomFilterEqual(FilterEqual):
    def apply(self, query, value):
        flt = get_flt(self.column, value)
        return query.filter(flt)


class CustomFilterNotEqual(FilterNotEqual):
    def apply(self, query, value):
        flt = get_flt(self.column, value, 'ne')
        return query.filter(flt)


class CustomFilterLike(FilterLike):
    def apply(self, query, value):
        term, data = parse_like_term(value)
        flt = get_flt(self.column, data, term)
        return query.filter(flt)


class CustomFilterNotLike(FilterNotLike):
    def apply(self, query, value):
        term, data = parse_like_term(value)
        flt = get_flt(self.column, data, 'not__%s' % term)
        return query.filter(flt)


class CustomFilterEmpty(FilterEmpty):
    def apply(self, query, value):
        if value == '1':
            flt = get_flt(self.column, None)
        else:
            flt = get_flt(self.column, None, 'ne')
        return query.filter(flt)


class CustomFilterInList(FilterInList):
    def apply(self, query, value):
        flt = get_flt(self.column, value, 'in')
        return query.filter(flt)


class CustomFilterNotInList(FilterNotInList):
    def apply(self, query, value):
        flt = get_flt(self.column, value, 'nin')
        return query.filter(flt)


class CustomFilterConverter(FilterConverter):
    # Campos dentro filtros ReferenceField, EmbeddedDocumentField, ListField
    # deve ser do tipo StringField

    reference_filters = (CustomFilterLike, CustomFilterNotLike, CustomFilterEqual,
                         CustomFilterNotEqual, CustomFilterEmpty, CustomFilterInList,
                         CustomFilterNotInList)
    list_filters = (CustomFilterLike, CustomFilterNotLike, CustomFilterEmpty)

    @filters.convert('ReferenceField', 'EmbeddedDocumentField')
    def conv_reference(self, column, name):
        return [f(column, name) for f in self.reference_filters]

    @filters.convert('ListField')
    def conv_list(self, column, name):
        return [f(column, name) for f in self.list_filters]
