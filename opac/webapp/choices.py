# coding: utf-8

from flask_babelex import gettext as _

UNPUBLISH_REASONS = [
    _(u'Problema de Direito Autoral'),
    _(u'Plágio'),
    _(u'Abuso ou Conteúdo Indevido'),
]

LANGUAGES_CHOICES = [
    ('pt_BR', _(u'Português')),
    ('en', _(u'Inglês')),
    ('es', _(u'Espanhol')),
]

INDEX_NAME = {
    'SCIE':  u'Science Citation Index',
    'SSCI':  u'Social Science Citation',
    'A&HCI':  u'Arts & Humanities Citation',
}

MONTHS = {
          1: _('jan'),
          2: _('fev'),
          3: _('mar'),
          4: _('abr'),
          5: _('mai'),
          6: _('jun'),
          7: _('jul'),
          8: _('aug'),
          9: _('set'),
          10: _('out'),
          11: _('nov'),
          12: _('dez')
}


ISO3166_ALPHA2 = {
    'pt': _(u'Português'),
    'en': _(u'Inglês'),
    'es': _(u'Espanhol'),
    'al': _(u'Albanês'),
    'cn': _(u'Chinês'),
    'ro': _(u'Romeno'),
    'fr': _(u'Francês'),
    'it': _(u'Italiano'),
    'ru': _(u'Russo'),
    'ar': _(u'Árabe'),
    'zh': _(u'Chinês'),
}
