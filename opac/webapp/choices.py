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

LICENSE_CHOICES = [
    ('BY/3.0', u'BY/3.0'),
    ('BY/3.0/IGO', u'BY/3.0/IGO'),
    ('BY/4.0', u'BY/4.0'),
    ('BY-NC/3.0', u'BY-NC/3.0 '),
    ('BY-NC/3.0/IGO', u'BY-NC/3.0/IGO '),
    ('BY-NC/4.0', u'BY-NC/4.0 '),
    ('BY-NC-ND/3.0 ', u'BY-NC-ND/3.0'),
    ('BY-NC-ND/3.0/IGO ', u'BY-NC-ND/3.0/IGO'),
    ('BY-NC-ND/4.0 ', u'BY-NC-ND/4.0'),
    ('BY-NC-SA/4.0 ', u'BY-NC-SA/4.0'),
    ('BY-ND/3.0', u'BY-ND/3.0 '),
    ('BY-ND/4.0 ', u'BY-ND/4.0')
]
