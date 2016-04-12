# coding: utf-8

from flask_babelex import gettext as _

UNPUBLISH_REASONS = [
    _(u'Problema de Direito Autoral'),
    _(u'Plágio'),
    _(u'Abuso ou Conteúdo Indevido'),
]

RESOURCE_TYPE_CHOICES = [
    ('img', _(u'Imagem')),
    ('pdf', _(u'PDF')),
    ('html', _(u'HTML')),
    ('file', _(u'Arquivo')),
    ('link', _(u'Link')),
    ('other', _(u'Outros')),
]

RESOURCE_LANGUAGES_CHOICES = [
    ('pt_BR', _(u'Português')),
    ('en', _(u'Inglês')),
    ('es', _(u'Español')),
]
