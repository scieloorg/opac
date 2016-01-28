# coding: utf-8
import logging
from mongoengine import ReferenceField, EmbeddedDocumentField
from mongoengine.queryset import Q
from opac_schema.v1.models import Journal


def get_flt(column=None, value=None, term=''):
    flt = None
    search_fields = {
        'journal': ['jid', 'title', 'title_iso', 'short_title', 'acronym', 'print_issn', 'eletronic_issn'],
        'use_licenses': ['license_code']
    }
    if isinstance(column, ReferenceField) and isinstance(column.document_type_obj(), Journal):
        criteria = None
        for field in search_fields['journal']:
            flt = {'%s__%s' % (field, term): value}
            q = Q(**flt)

            if criteria is None:
                criteria = q
            elif term in ['ne', 'not__contains', 'nin']:
                criteria &= q
            else:
                criteria |= q
        journal = Journal.objects.filter(criteria)
        flt = {'journal__in': journal}

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
    else:
        flt = {'%s__%s' % (column.name, term): value}

    return Q(**flt)
