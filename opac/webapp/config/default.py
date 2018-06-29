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
        - OPAC_USE_METRICS:   ativa/desativa a integração com o SciELO Analytics. Se sim, definir como 'True' (default: 'False')
        - OPAC_METRICS_URL:   URL para SciELO Analytics (default: 'http://analytics.scielo.org')
        - OPAC_USE_DIMENSIONS:   ativa/desativa a integração com o Dimensions. Se sim, definir como 'True' (default: 'False')
        - OPAC_USE_PLUMX:    ativa/desativa a integração com o PlumX. Se sim, definir como 'True' (default: 'False')
        - OPAC_PLUMX_METRICS_URL:   URL para o PlumX (default: https://plu.mx/scielo/a)

      - Timezone:
        - LOCAL_ZONE: Default 'America/Sao_Paulo'

      - Sentry
        - OPAC_USE_SENTRY:  ativa/desativa a integarção com Sentry, se sim definir como: 'True' (default: 'False')
        - OPAC_SENTRY_DSN: (string) DSN definido pelo sentry para este projeto. Utilizado só se OPAC_USE_SENTRY == True  (default: '')

      - docker build args (ignorar warnings na construção de imagem para desenvolvimento)
        - OPAC_BUILD_DATE: data de build. definida em tempo de construção da imagem.
        - OPAC_VCS_REF: commit do código. definida pelo travis em tempo de construção da imagem.
        - OPAC_WEBAPP_VERSION: 'versão do OPAC WEBAPP'. definida pelo travis em tempo de construção da imagem.

      - CSRF
        - OPAC_WTF_CSRF_ENABLED: ativa/desativa o recurso de CSRF (default: True)
        - OPAC_WTF_CSRF_SECRET_KEY: chave para segurança nos formulários WTF. (default: JGvNWiwBIq2Iig89LWbV)

      - ReadCube:
        - READCUBE_ENABLED: ativa/desativa a exibição do link para o ReadCube, se sim definir como: 'True' (default: 'False')

      - Conexão com SSM:
        - OPAC_SSM_SCHEME: Protocolo de conexão com SSM. Opções: 'http' ou 'https' - (default: 'https')
        - OPAC_SSM_DOMAIN: Dominio/FQDN do conexão com SSM. Ex: 'homolog.ssm.scielo.org - (default: 'ssm.scielo.org')
        - OPAC_SSM_PORT: Porta de conexão com o SSM. Ex. '8000'. (default: '80')
        - OPAC_SSM_MEDIA_PATH: Path da pasta media do assests no SSM. Ex. '/media/assets/' -  (default: '/media/assets/')

      - Cookie de Sessão: (http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values)
        - OPAC_SERVER_NAME: Nome:IP do servidor - (default: None)
        - OPAC_SESSION_COOKIE_DOMAIN: o dominio para a cookie da sessão (default: OPAC_SERVER_NAME)
        - OPAC_SESSION_COOKIE_HTTPONLY: Seta a flag: httponly da cookie. (defaults to True)
        - OPAC_SESSION_COOKIE_NAME: nome da cookie de sessão (default: 'opac_session')
        - OPAC_SESSION_COOKIE_PATH: path para a cookie de sessão: (default: None -> ou seja a raiz /)
        - OPAC_SESSION_COOKIE_SECURE: define se a cookie de sessão deve ser marcada como segura - (default: False)
        - OPAC_SESSION_REFRESH_EACH_REQUEST: Fazer refresh da cookie em cada request? (Default: 'False')

      - Cache da app: https://pythonhosted.org/Flask-Caching/
        - OPAC_CACHE_ENABLED: ativa/desativa o cache com redis (default: True)
        - OPAC_CACHE_TYPE: o tipo de backend do cache: 'null', 'redis', outros (default: 'redis')
        - OPAC_CACHE_NO_NULL_WARNING: ativa/desativa exibição de warnings quando o CACHE_TYPE é 'null' (default: True)
        - OPAC_CACHE_DEFAULT_TIMEOUT: tempo de vida dos objetos no cache. Tempo medido em segundos (default: 3600)
        - OPAC_CACHE_KEY_PREFIX: prefixo da chave de cache. (default: 'opac_cache')
        - OPAC_CACHE_REDIS_HOST: host do servidor redis que vai ser usado no cache. (default: 'redis-cache')
        - OPAC_CACHE_REDIS_PORT: porta do servidor redis que vai ser usado no cache. (default: 6379)
        - OPAC_CACHE_REDIS_DB: nome de db do servidor redis que vai ser usado no cache (inteiro >= 0). (default: 0)
        - OPAC_CACHE_REDIS_PASSWORD: senha do servidor redis que vai ser usado no cache. (default = '')

      - Pindom visitor insights:
        - OPAC_PINGDOM_VISITOR_INSIGHTS_JS_SRC: URL do JS para utilizar o Pingdom visitor insights (ex: `//rum-static.pingdom.net/pa-XXXXXXXXX.js`) (default: None)

      - Google reCAPTCHA:
        - OPAC_GOOGLE_RECAPTCHA_SECRET_KEY: Chave do site
        - OPAC_GOOGLE_VERIFY_RECAPTCHA_KEY Chave secreta do parceiro
        - OPAC_GOOGLE_RECAPTCHA_URL: URL do JavaScript Google reCAPTCHA
        - OPAC_GOOGLE_VERIFY_RECAPTCHA_URL: URL de verificação do google (default: https://www.google.com/recaptcha/api/siteverify )

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
    # 'es_ES': 'Español (España)',
    # 'es_MX': 'Español (México)',
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
PAGE_PATH = os.path.abspath(os.path.join(PROJECT_PATH, '../../data/pages'))

# extensions
FILES_ALLOWED_EXTENSIONS = ('txt', 'pdf', 'csv', 'xls', 'doc', 'ppt', 'xlsx', 'docx', 'pptx', 'html', 'htm')
IMAGES_ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif', 'webp')
IMAGES_ALLOWED_EXTENSIONS_RE = tuple('*.' + ext for ext in IMAGES_ALLOWED_EXTENSIONS)
THUMBNAIL_HEIGHT = 100
THUMBNAIL_WIDTH = 100

# search scielo
URL_SEARCH = os.environ.get('OPAC_URL_SEARCH', '//search.scielo.org/')

# analytics scielo
USE_METRICS = os.environ.get('OPAC_USE_METRICS', 'False') == 'True'
METRICS_URL = os.environ.get('OPAC_METRICS_URL', 'http://analytics.scielo.org')

# third-party metrics
USE_DIMENSIONS = os.environ.get('OPAC_USE_DIMENSIONS', 'False') == 'True'
USE_PLUMX = os.environ.get('OPAC_USE_PLUMX', 'False') == 'True'
PLUMX_METRICS_URL = os.environ.get('OPAC_PLUMX_METRICS_URL', 'https://plu.mx/scielo/a')

NEWS_LIST_LIMIT = 10

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

# CSRF
OPAC_WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True') == 'True'

# CSRF secret
OPAC_WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'JGvNWiwBIq2Iig89LWbV')
READCUBE_ENABLED = os.environ.get('OPAC_READCUBE_ENABLED', 'False') == 'True'

# Conf de conexão com o SSM (pdfs e imagens)
SSM_SCHEME = os.environ.get('OPAC_SSM_SCHEME', 'https')
SSM_DOMAIN = os.environ.get('OPAC_SSM_DOMAIN', 'homolog.ssm.scielo.org')
SSM_PORT = os.environ.get('OPAC_SSM_PORT', '443')
SSM_MEDIA_PATH = os.environ.get('OPAC_SSM_MEDIA_PATH', '/media/assets/')

# SSM_BASE_URI ex: 'https://homolog.ssm.scielo.org:80/'
SSM_BASE_URI = "{scheme}://{domain}:{port}".format(
  scheme=SSM_SCHEME,
  domain=SSM_DOMAIN,
  port=SSM_PORT)

# SSM_BASE_URI ex: 'https://homolog.ssm.scielo.org:80/media/assets/'
SSM_MEDIA_URI = "{scheme}://{domain}:{port}{path}".format(
  scheme=SSM_SCHEME,
  domain=SSM_DOMAIN,
  port=SSM_PORT,
  path=SSM_MEDIA_PATH)

# session cookie settings:

SERVER_NAME = os.environ.get('OPAC_SERVER_NAME', None)
SESSION_COOKIE_DOMAIN = os.environ.get('OPAC_SESSION_COOKIE_DOMAIN', SERVER_NAME)
SESSION_COOKIE_HTTPONLY = os.environ.get('OPAC_SESSION_COOKIE_HTTPONLY', 'True') == 'True'
SESSION_COOKIE_NAME = os.environ.get('OPAC_SESSION_COOKIE_NAME', 'opac_session')
SESSION_COOKIE_PATH = os.environ.get('OPAC_SESSION_COOKIE_PATH', None)
SESSION_COOKIE_SECURE = os.environ.get('OPAC_SESSION_COOKIE_SECURE', 'False') == 'True'
SESSION_REFRESH_EACH_REQUEST = os.environ.get('OPAC_SESSION_REFRESH_EACH_REQUEST', 'False') == 'True'


# Flask Caching:

CACHE_ENABLED = os.environ.get('OPAC_CACHE_ENABLED', 'False') == 'True'
CACHE_TYPE = os.environ.get('OPAC_CACHE_TYPE', 'redis')
CACHE_NO_NULL_WARNING = os.environ.get('OPAC_CACHE_NO_NULL_WARNING', 'True') == 'True'
CACHE_DEFAULT_TIMEOUT = os.environ.get('OPAC_CACHE_DEFAULT_TIMEOUT', 3600)  # segundos
CACHE_KEY_PREFIX = os.environ.get('OPAC_CACHE_KEY_PREFIX', 'opac_cache')
CACHE_REDIS_HOST = os.environ.get('OPAC_CACHE_REDIS_HOST', 'redis-cache')
CACHE_REDIS_PORT = os.environ.get('OPAC_CACHE_REDIS_PORT', 6379)
CACHE_REDIS_DB = os.environ.get('OPAC_CACHE_REDIS_DB', '0')
CACHE_REDIS_PASSWORD = os.environ.get('OPAC_CACHE_REDIS_PASSWORD', None)

# Pingdom Visitor Insights:
PINGDOM_VISITOR_INSIGHTS_JS_SRC = os.environ.get('OPAC_PINGDOM_VISITOR_INSIGHTS_JS_SRC', None)

# Google Recaptcha
GOOGLE_RECAPTCHA_SECRET_KEY = os.environ.get('OPAC_GOOGLE_RECAPTCHA_SECRET_KEY', "")
GOOGLE_RECAPTCHA_URL = os.environ.get('OPAC_GOOGLE_RECAPTCHA_URL', "https://www.google.com/recaptcha/api.js")
GOOGLE_VERIFY_RECAPTCHA_URL = os.environ.get('OPAC_GOOGLE_VERIFY_RECAPTCHA_URL', "https://www.google.com/recaptcha/api/siteverify")
GOOGLE_VERIFY_RECAPTCHA_KEY = os.environ.get('OPAC_GOOGLE_VERIFY_RECAPTCHA_KEY', "")
