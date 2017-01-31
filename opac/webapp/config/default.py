# coding: utf-8

import os

"""
  Na Configuração padrão, definimos estas configurações para deixar a app rodando em modo "produção".
  Porém é recomendado ajustar algumas configuração para deixar uma instalação segura e
  funcional no seu ambiente, por exemplo definindo a coleção que o site deve atender.

  Para saber mais sobre configuração, visite:
      - http://flask.pocoo.org/docs/0.10/config/#builtin-configuration-values
      - https://pythonhosted.org/flask-mail/#configuring-flask-mail
      - http://flask-sqlalchemy.pocoo.org/2.1/config/
      - https://flask-mongoengine.readthedocs.org/en/latest/#configuration

  Para ajustar configurações, pode definir as variáveis de ambiente (ver abaixo) no seu host,
  ou copie o template que melhor se ajuste a seu ambiente, e apontando o caminho absoluto
  na variável de ambiente: **OPAC_CONFIG**, por exemplo:

      1. copiar este template: ``cp opac/config/templates/development.template /foo/var/baz/opac.config.py``
      2. editar: ``vim /foo/var/baz/opac.config.py``, pode consultar o arquivo: ``opac/webapp/config/default.py``
      3. definir a variável de ambiente **OPAC_CONFIG**: ``export OPAC_CONFIG="/foo/var/baz/opac.config.py"``
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
        - OPAC_MONGODB_USER:    [opcional] usuário para acessar o banco (default: None)
        - OPAC_MONGODB_PASS:    [opcional] password para acessar o banco (default: None)

      - Banco SQL:
        - OPAC_DATABASE_FILE:   nome do arquivo (sqlite) (default: 'opac.sqlite')
        - OPAC_DATABASE_DIR:    pasta aonde fica o banco (sqlite) (default: '/tmp')
        - OPAC_DATABASE_URI:    [opcional] URI do banco sql (default: 'sqlite:////tmp/opac.sqlite')

      - Google Analytics:
        - GA_TRACKING_CODE:     código de google analytics (acesse https://goo.gl/HE77SO para resgatar seu código)

      - Upload de imagens:
        - OPAC_MEDIA_ROOT:      path absoluto da pasta que vai armazenar as imagens subidas pelos usuários pelo admin.
                                (default: /[repo dir]/opac/opac/webapp/media/)
        - OPAC_MEDIA_URL:       URL para servir as imagens. (default: '/media')

      - Extensions:
        - FILES_ALLOWED_EXTENSIONS:  extensão dos arquivos permitidos para upload
        - IMAGES_ALLOWED_EXTENSIONS:  extensão imagens permitidas para upload
        - THUMBNAIL_HEIGHT:     altura do thumbnail
        - THUMBNAIL_HEIGHT:     largura do thumbnail

      - Twitter:
        - OPAC_TWITTER_CONSUMER_KEY:    Twitter comuser key (default: 'consum3r-k3y')
        - OPAC_TWITTER_CONSUMER_SECRET: Twitter comuser secret (default: 'consum3r-secr3t')
        - OPAC_TWITTER_ACCESS_TOKEN:    Twitter access token (default: 'acc3ss-tok3n-secr3t')
        - OPAC_TWITTER_ACCESS_TOKEN_SECRET: Twitter access token (default: 'acc3ss-tok3n-secr3t')
        - OPAC_TWITTER_SCREEN_NAME: Twitter screen name (default: 'RedeSciELO')

      - Metrics:
        - OPAC_METRICS_URL:   URL para SciELO Analytics (default: 'http://analytics.scielo.org')

      - Timezone:
        - LOCAL_ZONE: Default 'America/Sao_Paulo'

      - Sentry
        - OPAC_USE_SENTRY:  ativa/desativa a integarção com Sentry, se sim definir como: 'True' (default: 'False')
        - OPAC_SENTRY_DSN: (string) DSN definido pelo sentry para este projeto. Utilizado só se OPAC_USE_SENTRY == True  (default: '')

      - docker build args (ignorar warnings na construção de imagem para desenvolvimento)
        - OPAC_BUILD_DATE: data de build. definida em tempo de construção da imagem.
        - OPAC_VCS_REF: commit do código. definida pelo travis em tempo de construção da imagem.
        - OPAC_WEBAPP_VERSION: 'versão do OPAC WEBAPP'. definida pelo travis em tempo de construção da imagem.
"""

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HERE = os.path.dirname(os.path.abspath(__file__))

# ativa/desativa o modo Debug da app
# NUNCA deixar DEBUG = 'True' em produção
# OPAC_DEBUG_MODE DEVE SER SEMPRE UM STRING 'False' OR 'True'
DEBUG = os.environ.get('OPAC_DEBUG_MODE', 'False') == 'True'

# ativa/desativa o modo Testing da app
# NUNCA deixar TESTING = True em produção
TESTING = False


# ativa/desativa o modo Debug dos assets
# NUNCA deixar ASSETS_DEBUG = True em produção
ASSETS_DEBUG = DEBUG


# ativa/desativa o modo Debug mimificado do HTML
MINIFY_PAGE = True


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
SQLALCHEMY_DATABASE_URI = os.environ.get('OPAC_DATABASE_URI', 'sqlite:////%s' % DATABASE_PATH)
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False


# Tempo de expiração para os tokens
# valor en segundos: 86400 = 60*60*24 = 1 dia
TOKEN_MAX_AGE = 86400


# Linguagens suportados
LANGUAGES = {
    'pt_BR': 'Português',
    'en': 'English',
    'es': 'Español',
    'es_ES': 'Español (España)',
    'es_MX': 'Español (México)',
}

# linguagem padrão:
BABEL_DEFAULT_LOCALE = 'pt_BR'

# Horário local
LOCAL_ZONE = os.environ.get('LOCAL_ZONE', 'America/Sao_Paulo')

# Código Google Analytics:
# -*- DEVE SER AJUSTADO NA INSTALAÇÃO -*-
GA_TRACKING_CODE = os.environ.get('GA_TRACKING_CODE', None)


# debug toolbar:
DEBUG_TB_INTERCEPT_REDIRECTS = False

# media files
DEFAULT_MEDIA_ROOT = os.path.abspath(os.path.join(PROJECT_PATH, 'media'))
MEDIA_ROOT = os.environ.get('OPAC_MEDIA_ROOT', DEFAULT_MEDIA_ROOT)
IMAGE_ROOT = os.path.join(MEDIA_ROOT, 'images')
FILE_ROOT = os.path.join(MEDIA_ROOT, 'files')
MEDIA_URL = os.environ.get('OPAC_MEDIA_URL', '/media')

# extensions
FILES_ALLOWED_EXTENSIONS = ('txt', 'pdf', 'csv', 'xls', 'doc', 'ppt', 'xlsx', 'docx', 'pptx', 'html', 'htm')
IMAGES_ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif', 'webp')
IMAGES_ALLOWED_EXTENSIONS_RE = tuple('*.' + ext for ext in IMAGES_ALLOWED_EXTENSIONS)
THUMBNAIL_HEIGHT = 100
THUMBNAIL_WIDTH = 100

# search scielo
URL_SEARCH = os.environ.get('OPAC_URL_SEARCH', 'http://search.scielo.org/')

# analytics scielo
OPAC_METRICS_URL = os.environ.get('OPAC_METRICS_URL', 'http://analytics.scielo.org')

NEWS_LIST_LIMIT = 10
RSS_NEWS_FEEDS = {
    'pt_BR': {
        'display_name': 'SciELO em Perspectiva',
        'url': 'http://blog.scielo.org/feed/'
    },
    'es': {
        'display_name': 'SciELO en Perspectiva',
        'url': 'http://blog.scielo.org/es/feed/',
    },
    'en': {
        'display_name': 'SciELO in Perspective',
        'url': 'http://blog.scielo.org/en/feed/',
    },
}

RSS_PRESS_RELEASES_FEEDS = {
    'pt_BR': {
        'display_name': 'SciELO em Perspectiva Press Releases',
        'url': 'http://pressreleases.scielo.org/feed/'
    },
    'es': {
        'display_name': 'SciELO en Perspectiva Press Releases',
        'url': 'http://pressreleases.scielo.org/es/feed/',
    },
    'en': {
        'display_name': 'SciELO in Perspective Press Releases',
        'url': 'http://pressreleases.scielo.org/en/feed/',
    },
}

RSS_PRESS_RELEASES_FEEDS_BY_CATEGORY = {
    'pt_BR': {
        'display_name': 'SciELO em Perspectiva Press Releases',
        'url': 'http://pressreleases.scielo.org/blog/category/{1}/feed/'
    },
    'es': {
        'display_name': 'SciELO en Perspectiva Press Releases',
        'url': 'http://pressreleases.scielo.org/{0}/category/press-releases/{1}/feed/',
    },
    'en': {
        'display_name': 'SciELO in Perspective Press Releases',
        'url': 'http://pressreleases.scielo.org/{0}/category/press-releases/{1}/feed/',
    },
}

# paineis do flask-debug-toolbar somente ativos quando DEBUG = True

DEBUG_TB_PANELS = [
    # default:
    'flask_debugtoolbar.panels.versions.VersionDebugPanel',
    'flask_debugtoolbar.panels.timer.TimerDebugPanel',
    'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
    'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
    'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
    'flask_debugtoolbar.panels.template.TemplateDebugPanel',
    'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
    'flask_debugtoolbar.panels.logger.LoggingPanel',
    'flask_debugtoolbar.panels.route_list.RouteListDebugPanel',
    'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
    # Mongo:
    # 'flask_mongoengine.panels.MongoDebugPanel'
]


# Configurações do API Twitter
TWITTER_CONSUMER_KEY = os.environ.get('OPAC_TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = os.environ.get('OPAC_TWITTER_CONSUMER_SECRET', '')
TWITTER_ACCESS_TOKEN = os.environ.get('OPAC_TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('OPAC_TWITTER_ACCESS_TOKEN_SECRET', '')
TWITTER_SCREEN_NAME = os.environ.get('OPAC_TWITTER_SCREEN_NAME', 'RedeSciELO')
TWITTER_LIMIT = '10'

# Sentry settings:
USE_SENTRY = os.environ.get('OPAC_USE_SENTRY', 'False') == 'True'
SENTRY_DSN = os.environ.get('OPAC_SENTRY_DSN', '')

# build args:
BUILD_DATE = os.environ.get('OPAC_BUILD_DATE', None)
VCS_REF = os.environ.get('OPAC_VCS_REF', None)
WEBAPP_VERSION = os.environ.get('OPAC_WEBAPP_VERSION', None)
