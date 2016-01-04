# coding: utf-8

"""
    Configuração padrão, não depende do ambiente (produção, development, etc)
"""

DEBUG = False
MAIL_FROM_EMAIL = "default@scielo.org"

SECRET_KEY = '02ee54614563e5946b1497b0ba07c24a'

ASSETS_DEBUG = False

MONGODB_SETTINGS = {
    'db': 'opac',
    # 'host': '127.0.0.1',
    # 'port': 27017
}

# SQL Alchemy
DATABASE_FILE = 'opac_admin.sqlite'
DATABASE_DIR = '/tmp'  # Absoulte path
DATABASE_PATH = '%s/%s' % (DATABASE_DIR, DATABASE_FILE)
SQLALCHEMY_DATABASE_URI = 'sqlite:////%s' % DATABASE_PATH
SQLALCHEMY_ECHO = DEBUG

# Acrônimo da coleção OPAC: 'spa' ou 'esp' por exemplo.
OPAC_COLLECTION = ''

# Tempo de expiração para os tokens
TOKEN_MAX_AGE = 86400  # valor en segundos: 86400 = 60*60*24 = 1 dia
