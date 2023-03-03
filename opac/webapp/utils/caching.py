# Redis Cache Key Generation:
import hashlib

from flask import current_app, request, session


def _make_querystring_hash():
    """
    Função que gera o hash a partir dos dados da querystring do request
    """

    args_as_sorted_tuple = tuple(
        sorted((pair for pair in request.args.items(multi=True)))
    )
    args_as_bytes = str(args_as_sorted_tuple).encode()
    return str(hashlib.md5(args_as_bytes).hexdigest())


def _cache_key_format(lang_code, request_path, qs_hash=None):
    """
    função que retorna o string que será a chave no cache.
    formata o string usando os parâmetros da função:
    - lang_code: código do idioma: [pt_BR|es|en]
    - request_path: o path do request
    - qs_hash: o hash gerado a partir dos parametros da querystring (se não for None)
    """

    cache_key = "/LANG=%s/PATH=%s" % (lang_code, request_path)
    if qs_hash is not None:
        cache_key = "%s?QS=%s" % (cache_key, qs_hash)
    return cache_key


def cache_key_with_lang():
    """
    Função chamada no decorator @cache.cached
    Retorna a chave para usar no cache (redis) usando:
    - o códiog do idioma armazenado na sessão (ou o default se não tiver)
    - o path do request
    """

    default_lang = current_app.config.get("BABEL_DEFAULT_LOCALE")
    language = session.get("lang", default_lang)
    return _cache_key_format(language, request.path)


def cache_key_with_lang_with_qs():
    """
    Função chamada no decorator @cache.cached
    Retorna a chave para usar no cache (redis) usando:
    - o códiog do idioma armazenado na sessão (ou o default se não tiver)
    - o path do request
    - o hash gerado a partir dos parametros da querystring
    """

    default_lang = current_app.config.get("BABEL_DEFAULT_LOCALE")
    language = session.get("lang", default_lang)
    qs_hash = _make_querystring_hash()
    return _cache_key_format(language, request.path, qs_hash)
