# coding: utf-8

from flask_babelex import gettext as _
from flask_babelex import lazy_gettext as __

UNPUBLISH_REASONS = [
    _("Conteúdo temporariamente indisponível"),
]

LANGUAGES_CHOICES = [
    ("pt_BR", __("Português")),
    ("en", __("Inglês")),
    ("es", __("Espanhol")),
]

INDEX_NAME = {
    "SCIE": "Science Citation Index",
    "SSCI": "Social Science Citation",
    "A&HCI": "Arts & Humanities Citation",
}

ISO3166_ALPHA2 = {
    "pt": __("Português"),
    "en": __("Inglês"),
    "es": __("Espanhol"),
    "al": __("Albanês"),
    "cn": __("Chinês"),
    "ro": __("Romeno"),
    "fr": __("Francês"),
    "it": __("Italiano"),
    "ru": __("Russo"),
    "ar": __("Árabe"),
    "zh": __("Chinês"),
}

JOURNAL_STATUS = {
    "current": __("corrente"),
    "deceased": __("terminado"),
    "suspended": __("indexação interrompida"),
    "interrupted": __("indexação interrompida pelo Comitê"),
    "finished": __("publicação finalizada"),
}

STUDY_AREAS = {
    "AGRICULTURAL SCIENCES": __("Ciências Agrárias"),
    "APPLIED SOCIAL SCIENCES": __("Ciências Sociais Aplicadas"),
    "BIOLOGICAL SCIENCES": __("Ciências Biológicas"),
    "ENGINEERING": __("Engenharias"),
    "EXACT AND EARTH SCIENCES": __("Ciências Exatas e da Terra"),
    "HEALTH SCIENCES": __("Ciências da Saúde"),
    "HUMAN SCIENCES": __("Ciências Humanas"),
    "LINGUISTICS, LETTERS AND ARTS": __("Lingüística, Letras e Artes"),
    "LINGUISTICS, LITERATURE AND ARTS": __("Lingüística, Letras e Artes"),
}
