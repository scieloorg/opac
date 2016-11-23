# coding: utf-8

from flask_babelex import gettext as _
from flask_babelex import lazy_gettext as __

UNPUBLISH_REASONS = [
    _(u'Problema de Direito Autoral'),
    _(u'Plágio'),
    _(u'Abuso ou Conteúdo Indevido'),
]

LANGUAGES_CHOICES = [
    ('pt_BR', __(u'Português')),
    ('en', __(u'Inglês')),
    ('es', __(u'Espanhol')),
]

INDEX_NAME = {
    'SCIE':  u'Science Citation Index',
    'SSCI':  u'Social Science Citation',
    'A&HCI':  u'Arts & Humanities Citation',
}

ISO3166_ALPHA2 = {
    'pt': __(u'Português'),
    'en': __(u'Inglês'),
    'es': __(u'Espanhol'),
    'al': __(u'Albanês'),
    'cn': __(u'Chinês'),
    'ro': __(u'Romeno'),
    'fr': __(u'Francês'),
    'it': __(u'Italiano'),
    'ru': __(u'Russo'),
    'ar': __(u'Árabe'),
    'zh': __(u'Chinês'),
}
