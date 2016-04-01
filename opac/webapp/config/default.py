# coding: utf-8

import os

"""
  Configuração padrão, definimos estas configurações para deixar a app rodando como produção.
  Porém é necessário ajustar algumas configuração para deixar uma instalação segura e
  funcional no seu ambiente, por exemplo definindo a coleção que o site deve atender.

  Para saber mais sobre configuração, visite:
      - http://flask.pocoo.org/docs/0.10/config/#builtin-configuration-values
      - https://pythonhosted.org/flask-mail/#configuring-flask-mail
      - http://flask-sqlalchemy.pocoo.org/2.1/config/
      - https://flask-mongoengine.readthedocs.org/en/latest/#configuration

  Para ajustar configurações, pode definir as variáveis de ambiante (ver abaixo) no seu host,
  ou copie o template que melhor se ajuste a seu ambiente, e apontando o caminho absoluto
  na variável de ambiente: OPAC_CONFIG, por exemplo:

      1. copiar este template: ``cp opac/config/templates/development.template /foo/var/baz/opac.config.py``
      2. editar: ``vim /foo/var/baz/opac.config.py``, pode consultar o arquivo: opac/config/default.py
      3. definir a variável de ambiente OPAC_CONFIG: ``export OPAC_CONFIG="/foo/var/baz/opac.config.py"``
      4. iniciar/reiniciar o servidor web

  Variavies de ambiente:

      - Modo Debug:
        - OPAC_DEBUG_MODE:      ativa/desativa o modo Debug da app, deve estar desativado em produção! (default: False)

      - Segurança:
        - OPAC_SECRET_KEY:      chave necessária para segurança nos formulario da app.

      - Coleção:
        - OPAC_COLLECTION: acrônimo da coleção do opac (default: 'spa')

      - Para envio de emails:
        - OPAC_DEFAULT_EMAIL:   conta de email para envio de mensagens desde o site (default: 'scielo@scielo.org')
        - OPAC_MAIL_SERVER:     host do servidor de emails (default: localhost)
        - OPAC_MAIL_PORT:       porta do servidor de emails (default: 1025)
        - OPAC_MAIL_USE_TLS:    ativa/desativa envio de email com TLS (default: False)
        - OPAC_MAIL_USE_SSL:    ativa/desativa envio de email com SSL (default: False)

      - Banco Mongo:
        - OPAC_MONGODB_NAME:    nome do banco (default: 'opac')
        - OPAC_MONGODB_HOST:    host do banco (default: 'localhost')
        - OPAC_MONGODB_PORT:    porta do banco (default: 27017)
        - OPAC_MONGODB_USER:    [opcional] usuário para acessar o banco (defaul: None)
        - OPAC_MONGODB_PASS:    [opcional] password para acessar o banco (defaul: None)

      - Banco SQL:
        - OPAC_DATABASE_FILE:   nome do arquivo (sqlite) (default: 'opac.sqlite')
        - OPAC_DATABASE_DIR:    pasta aonde fica o banco (sqlite) (default: '/tmp')

      - Google Analytics:
        - GA_TRACKING_CODE:     código de google analytics (acesse https://goo.gl/HE77SO para resgatar seu código)

      - Upload de imagens:
        - OPAC_MEDIA_ROOT:      path absoluto da pasta que vai armazenar as imagens subidas pelos usuários pelo admin. (default: /[repo dir]/opac/opac/webapp/media/)
        - OPAC_MEDIA_URL:       URL para servir as imagens. (default: '/media')

"""

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HERE = os.path.dirname(os.path.abspath(__file__))

# ativa/desativa o modo Debug da app
# NUNCA deixar DEBUG = True em produção
DEBUG = bool(os.environ.get('OPAC_DEBUG_MODE', False))


# ativa/desativa o modo Testing da app
# NUNCA deixar TESTING = True em produção
TESTING = False


# ativa/desativa o modo Debug dos assets
# NUNCA deixar ASSETS_DEBUG = True em produção
ASSETS_DEBUG = DEBUG


# Email do webmaster, este e-mail será utilizado para contato em caso de página
# não encontrada e correções no conteúdo da aplicacão.
WEBMASTER_EMAIL = "webmaster@scielo.org"


# Acrônimo da coleção OPAC: 'spa' ou 'esp' por exemplo.
# -*- DEVE SER AJUSTADO NA INSTALAÇÃO -*-
OPAC_COLLECTION = os.environ.get('OPAC_COLLECTION', 'spa')


# Conta de email padrão para emails enviado do site - deve ser um email válido
DEFAULT_EMAIL = os.environ.get('OPAC_DEFAULT_EMAIL', 'scielo@scielo.org')


# Credenciais para envio de emails
# -*- DEVE SER AJUSTADO NA INSTALAÇÃO -*-
MAIL_SERVER = os.environ.get('OPAC_MAIL_SERVER', 'localhost')
MAIL_PORT = int(os.environ.get('OPAC_MAIL_PORT', 1025))
MAIL_USE_TLS = bool(os.environ.get('OPAC_MAIL_USE_TLS', False))
MAIL_USE_SSL = bool(os.environ.get('OPAC_MAIL_USE_SSL', False))
MAIL_DEBUG = DEBUG
MAIL_USERNAME = os.environ.get('OPAC_MAIL_USERNAME', None)
MAIL_PASSWORD = os.environ.get('OPAC_MAIL_PASSWORD', None)
MAIL_DEFAULT_SENDER = DEFAULT_EMAIL
MAIL_MAX_EMAILS = None
MAIL_ASCII_ATTACHMENTS = False


# sustituir o valor de SECRET_KEY,
# -*- DEVE SER AJUSTADO NA INSTALAÇÃO -*-
# para gerar um novo key, pode utilizar: https://gist.github.com/jfunez/873c78890d55354739c8
SECRET_KEY = os.environ.get('OPAC_SECRET_KEY', 'secr3t-k3y')


# Configurações do banco de dados Mongodb
# -*- DEVE SER AJUSTADO NA INSTALAÇÃO -*-
MONGODB_NAME = os.environ.get('OPAC_MONGODB_NAME', 'opac')
MONGODB_HOST = os.environ.get('OPAC_MONGODB_HOST', 'localhost')
MONGODB_PORT = os.environ.get('OPAC_MONGODB_PORT', 27017)
MONGODB_USER = os.environ.get('OPAC_MONGODB_USER', None)
MONGODB_PASS = os.environ.get('OPAC_MONGODB_PASS', None)

MONGODB_SETTINGS = {
    'db': MONGODB_NAME,
    'host': MONGODB_HOST,
    'port': int(MONGODB_PORT),
}

if MONGODB_USER and MONGODB_PASS:
    MONGODB_SETTINGS['username'] = MONGODB_USER
    MONGODB_SETTINGS['password'] = MONGODB_PASS


# Configurações do banco de dados SQL
# -*- DEVE SER AJUSTADO NA INSTALAÇÃO -*-
DATABASE_FILE = os.environ.get('OPAC_DATABASE_FILE', 'opac.sqlite')
DATABASE_DIR = os.environ.get('OPAC_DATABASE_DIR', '/tmp')  # Caminho absoluto da pasta que vai conter o arquivo sqlite
DATABASE_PATH = '%s/%s' % (DATABASE_DIR, DATABASE_FILE)
SQLALCHEMY_DATABASE_URI = os.environ.get('OPAC_DATABASE_FILE', 'sqlite:////%s' % DATABASE_PATH)
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False


# Tempo de expiração para os tokens
# valor en segundos: 86400 = 60*60*24 = 1 dia
TOKEN_MAX_AGE = 86400


# Linguagens suportados
LANGUAGES = {
    'pt_BR': u'Português',
    'en': u'English',
    'es': u'Español',
    'es_ES': u'Español (España)',
    'es_MX': u'Español (México)',
}

# linguagem padrão:
BABEL_DEFAULT_LOCALE = 'pt_BR'

# Código Google Analytics:
# -*- DEVE SER AJUSTADO NA INSTALAÇÃO -*-
GA_TRACKING_CODE = os.environ.get('GA_TRACKING_CODE', None)


# debug toolbar:
DEBUG_TB_INTERCEPT_REDIRECTS = False

# media files
DEFAULT_MEDIA_ROOT = os.path.abspath(os.path.join(PROJECT_PATH, 'media'))
MEDIA_ROOT = os.environ.get('OPAC_MEDIA_ROOT', DEFAULT_MEDIA_ROOT)
MEDIA_URL = os.environ.get('OPAC_MEDIA_URL', '/media')
