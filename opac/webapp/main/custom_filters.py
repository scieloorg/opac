# coding: utf-8

from webapp import choices
from webapp.utils import utc_to_local


def trans_alpha2(value):
    """
    Traduz siglas de idioma de 2 caracteres para nome.
    """

    if value in choices.ISO3166_ALPHA2:
        return choices.ISO3166_ALPHA2[value]
    else:
        return value


def datetimefilter(value, format="%Y-%m-%d %H:%M"):
    return utc_to_local(value).strftime(format)
