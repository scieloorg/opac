# coding: utf-8

from flask_admin.contrib import sqla
from flask_admin.contrib.mongoengine.filters import (
    FilterConverter,
    FilterEmpty,
    FilterEqual,
    FilterInList,
    FilterLike,
    FilterNotEqual,
    FilterNotInList,
    FilterNotLike,
)
from flask_admin.contrib.mongoengine.tools import parse_like_term
from flask_admin.model import filters
from mongoengine import EmbeddedDocumentField, ListField, ReferenceField, StringField
from mongoengine.queryset import Q
from opac_schema.v1.models import Issue, Journal
from webapp import models


def get_flt(column=None, value=None, term=""):
    flt = None
    search_fields = {
        "journal": [
            "title",
            "title_iso",
            "short_title",
            "acronym",
            "print_issn",
            "eletronic_issn",
        ],
        "issue": ["label"],
        "use_licenses": ["license_code", "reference_url", "disclaimer"],
    }

    if isinstance(column, ReferenceField):
        criteria = None
        reference_values = None
        for field in search_fields[column.name]:
            flt = {"%s__%s" % (field, term): value}
            q = Q(**flt)

            if criteria is None:
                criteria = q
            elif term in ["ne", "not__contains", "nin"]:
                criteria &= q
            else:
                criteria |= q
        if isinstance(column.document_type_obj(), Journal):
            reference_values = Journal.objects.filter(criteria)
        if isinstance(column.document_type_obj(), Issue):
            reference_values = Issue.objects.filter(criteria)
        flt = {"%s__in" % column.name: reference_values}

    elif isinstance(column, EmbeddedDocumentField):
        criteria = None
        for field in search_fields[column.name]:
            flt = {"%s__%s__%s" % (column.name, field, term): value}
            q = Q(**flt)

            if criteria is None:
                criteria = q
            elif term in ["ne", "not__contains", "nin"]:
                criteria &= q
            else:
                criteria |= q
        return criteria

    elif isinstance(column, ListField) and isinstance(column.field, StringField):
        flt = {"%s__%s" % (column.name, term): value if value else []}

    else:
        flt = {"%s__%s" % (column.name, term): value}

    return Q(**flt)


class CustomFilterEqual(FilterEqual):
    def apply(self, query, value):
        flt = get_flt(self.column, value)
        return query.filter(flt)


class CustomFilterNotEqual(FilterNotEqual):
    def apply(self, query, value):
        flt = get_flt(self.column, value, "ne")
        return query.filter(flt)


class CustomFilterLike(FilterLike):
    def apply(self, query, value):
        term, data = parse_like_term(value)
        flt = get_flt(self.column, data, term)
        return query.filter(flt)


class CustomFilterNotLike(FilterNotLike):
    def apply(self, query, value):
        term, data = parse_like_term(value)
        flt = get_flt(self.column, data, "not__%s" % term)
        return query.filter(flt)


class CustomFilterEmpty(FilterEmpty):
    def apply(self, query, value):
        if value == "1":
            flt = get_flt(self.column, None)
        else:
            flt = get_flt(self.column, None, "ne")
        return query.filter(flt)


class CustomFilterInList(FilterInList):
    def apply(self, query, value):
        flt = get_flt(self.column, value, "in")
        return query.filter(flt)


class CustomFilterNotInList(FilterNotInList):
    def apply(self, query, value):
        flt = get_flt(self.column, value, "nin")
        return query.filter(flt)


class CustomFilterConverter(FilterConverter):
    # Campos dentro filtros ReferenceField, EmbeddedDocumentField, ListField
    # deve ser do tipo StringField

    reference_filters = (
        CustomFilterLike,
        CustomFilterNotLike,
        CustomFilterEqual,
        CustomFilterNotEqual,
        CustomFilterInList,
        CustomFilterNotInList,
    )
    embedded_filters = (
        CustomFilterLike,
        CustomFilterNotLike,
        CustomFilterEqual,
        CustomFilterNotEqual,
        CustomFilterEmpty,
        CustomFilterInList,
        CustomFilterNotInList,
    )
    list_filters = (CustomFilterLike, CustomFilterNotLike, CustomFilterEmpty)

    @filters.convert("ReferenceField")
    def conv_reference(self, column, name):
        return [f(column, name) for f in self.reference_filters]

    @filters.convert("EmbeddedDocumentField")
    def conv_embedded(self, column, name):
        return [f(column, name) for f in self.embedded_filters]

    @filters.convert("ListField")
    def conv_list(self, column, name):
        return [f(column, name) for f in self.list_filters]


class CustomFilterConverterSqla(sqla.filters.FilterConverter):
    choice_filters = (
        sqla.filters.FilterEqual,
        sqla.filters.FilterNotEqual,
        sqla.filters.FilterEmpty,
        sqla.filters.FilterInList,
        sqla.filters.FilterNotInList,
    )

    choices = {
        "language": models.LANGUAGES_CHOICES,
    }

    @filters.convert("ChoiceType")
    def conv_choice(self, column, name, options):
        if not options:
            options = self.choices[column.name]
        return [f(column, name, options) for f in self.choice_filters]
