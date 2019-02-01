# coding: utf-8

from flask_babelex import gettext as _
from flask_babelex import lazy_gettext as __

UNPUBLISH_REASONS = [
    _('Conteúdo temporariamente indisponível'),
]

LANGUAGES_CHOICES = [
    ('pt_BR', __('Português')),
    ('en', __('Inglês')),
    ('es', __('Espanhol')),
]

INDEX_NAME = {
    'SCIE': 'Science Citation Index',
    'SSCI': 'Social Science Citation',
    'A&HCI': 'Arts & Humanities Citation',
}

ISO3166_ALPHA2 = {
    'pt': __('Português'),
    'en': __('Inglês'),
    'es': __('Espanhol'),
    'al': __('Albanês'),
    'cn': __('Chinês'),
    'ro': __('Romeno'),
    'fr': __('Francês'),
    'it': __('Italiano'),
    'ru': __('Russo'),
    'ar': __('Árabe'),
    'zh': __('Chinês'),
}

JOURNAL_STATUS = {
    "current": __("corrente"),
    "deceased": __("terminado"),
    "suspended": __("indexação interrompida"),
    "interrupted": __("indexação interrompida pelo Comitê"),
    "finished": __("publicação finalizada"),
}
