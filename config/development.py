# coding: utf-8

"""
    Configuração para o ambiente de desenvolvimento
"""


DEBUG = True
ASSETS_DEBUG = DEBUG


# envio de emails
MAIL_SERVER = 'localhost'
MAIL_PORT = 1025
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_DEBUG = DEBUG
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = 'webmaster.dev@opac.scielo.org'
MAIL_MAX_EMAILS = None
# MAIL_SUPPRESS_SEND = default app.testing
MAIL_ASCII_ATTACHMENTS = False
