# coding: utf-8

import choices


def abbrmonth(month_number):
    """
    Filtro para retorna o nome abreviado dos meses.

    month_number: parâmetro contendo o número do mês.
    """
    try:
        return choices.MONTHS[month_number]
    except KeyError:
        return ''
