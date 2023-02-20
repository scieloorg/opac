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

      - Home Metrics:
        - OPAC_USE_HOME_METRICS: ativa/desativa a apresentação dos dados de métricas da coleção (default: False),
                                 o padrão é não apresentar

      - Modo Debug:
        - OPAC_DEBUG_MODE:      ativa/desativa o modo Debug da app, deve estar desativado em produção! (default: False)

      - Segurança:
        - OPAC_SECRET_KEY:      chave necessária para segurança nos formulario da app.

      - Coleção:
        - OPAC_COLLECTION: acrônimo da coleção do opac (default: 'scl')

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
        - OPAC_DIMENSIONS_METRICS_URL:   URL para o Dimensions (default: https://badge.dimensions.ai/details/doi)
        - OPAC_USE_PLUMX:    ativa/desativa a integração com o PlumX. Se sim, definir como 'True' (default: 'False')
        - OPAC_PLUMX_METRICS_URL:   URL para o PlumX (default: https://plu.mx/a)
        - OPAC_PLUMX_METRICS_JS:   URL para o JS PlumX (default: //cdn.plu.mx/widget-popup.js)
        - OPAC_USE_SCIENCEOPEN:  ativa/desativa a integração de métricas com o ScienceOpen. Se sim, definir como 'True' (default: 'False')
        - OPAC_USE_SCITE:  ativa/desativa a integração de métricas com _SCITE. Se sim, definir como 'True' (default: 'False')
        - OPAC_SCITE_URL:  URL para o SCITE_ (default: https://cdn.scite.ai/badge/scite-badge-latest.min.js)
        - OPAC_SCITE_METRICS_URL: URL para o Scite_ (default: https://scite.ai/reports/)


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
        - OPAC_SSM_XML_URL_REWRITE: Troca o scheme + authority da URL armazenada em Article.xml por `OPAC_SSM_SCHEME + '://' + OPAC_SSM_DOMAIN + ':' + OPAC_SSM_PORT`. Variável booleana: 'False' (default: 'True')

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
        - OPAC_SEND_FILE_MAX_AGE_DEFAULT: define um valor inteiro padrão para os arquivos estáticos servido pelo Werkzeug. (default = 604800) valor em segundos 604800 é igual a uma semana
        - OPAC_CACHE_CONTROL_MAX_AGE_HEADER: define o tempo de cache para as páginas, response header Cache-Control: public, max-age={VALUE}, (default = 604800) valor em segundos 604800 é igual a uma semana

      - Pindom visitor insights:
        - OPAC_PINGDOM_VISITOR_INSIGHTS_JS_SRC: URL do JS para utilizar o Pingdom visitor insights (ex: `//rum-static.pingdom.net/pa-XXXXXXXXX.js`) (default: None)

      - Google reCAPTCHA:
        - OPAC_GOOGLE_RECAPTCHA_SECRET_KEY: Chave do site
        - OPAC_GOOGLE_VERIFY_RECAPTCHA_KEY Chave secreta do parceiro
        - OPAC_GOOGLE_RECAPTCHA_URL: URL do JavaScript Google reCAPTCHA
        - OPAC_GOOGLE_VERIFY_RECAPTCHA_URL: URL de verificação do google (default: https://www.google.com/recaptcha/api/siteverify )

      - Formulário de erro:
        - OPAC_EMAIL_ACCOUNTS_RECEIVE_ERRORS: # Contas de email para receber mensagens de erros da interface.

      - Auditoria:
        - OPAC_AUDIT_LOG_NOTIFICATION_ENABLED: (True/False) ativa/desativa envio de notificaçÕes via email do relatorio de auditoria
        - OPAC_AUDIT_LOG_NOTIFICATION_RECIPIENTS: (string), lista de email que devem receber o emails com relatorio de auditoria

      - Scheduler:
        - OPAC_RQ_REDIS_HOST: host do servidor de Redis (pode ser o mesmo server do Cache)
        - OPAC_RQ_REDIS_PORT: porta do servidor de Redis (pode ser o mesmo server do Cache)
        - OPAC_RQ_REDIS_PASSWORD: senha do servidor de Redis (pode ser o mesmo server do Cache)
        - OPAC_MAILING_CRON_STRING: valor de cron padrão para o envio de emails
        - OPAC_DEFAULT_SCHEDULER_TIMEOUT: timeout do screduler cron (dafault: 1000).

      - MathJax:
        - OPAC_MATHJAX_CDN_URL: string com a URL do mathjax padrão; ex: "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-AMS-MML_HTMLorMML"

      - Links SciELO:
        - URL_SCIELO_ORG: URL para o SciELO.org (default: '//www.scielo.org')
        - SCIELO_ORG_URIS: URIs em SciELO.org para sessões específicas
        - URL_BLOG_SCIELO: URL para o Blog SciELO em Perspectiva (default: '//blog.scielo.org')
        - URL_SEARCH: URL para o Search SciELO (default: '//search.scielo.org/')
        - URL_BLOG_PRESSRELEASE: URL para o Blog SciELO em Perspectiva Press releases (default: '//pressreleases.scielo.org')

      - Cookie Policy
        - OPAC_COOKIE_POLICY_ENABLED: ativa/desativa o javascript de política de cookie, se sim definir como: 'True' caso contrário 'False' (default: 'True')
        - OPAC_COOKIE_POLICY_URL: URL do script de política de cookie (default: https://static.scielo.org/js/cookiePolicy.min.js)

      - ORCID:
        - OPAC_ORCID_URL: URL do ORCID. (default: http://orcid.org/)

      - Google Meta tags (https://developers.google.com/search/docs/advanced/crawling/special-tags)
        - OPAC_FORCE_USE_HTTPS_GOOGLE_TAGS: Força o uso de https nas URLs para do site do OPAC nas tags do google. (default: True)

      - Issue TOC
        - OPAC_FILTER_SECTION_ENABLE: ativa/desativa o filtro por seção na página do issue.

      - Common Style List
        - OAPC_COMMON_STYLE_LIST: Caminho para um arquivo .json com as CSL.
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

# Define o nível do log para toda a aplicação e suas dependências
LOG_LEVEL = os.environ.get('OPAC_LOG_LEVEL', 'DEBUG' if DEBUG else 'WARNING')

# ativa/desativa o modo Debug dos assets
# NUNCA deixar ASSETS_DEBUG = True em produção
ASSETS_DEBUG = DEBUG


# ativa/desativa o modo Debug mimificado do HTML
MINIFY_PAGE = os.environ.get('OPAC_MINIFY_PAGE', 'False') == 'True'


# Email do webmaster, este e-mail será utilizado para contato em caso de página
# não encontrada e correções no conteúdo da aplicacão.
WEBMASTER_EMAIL = "webmaster@scielo.org"

# ativa/desativa a apresentação dos dados de métricas da coleção (default: False),
# o padrão é não apresentar
USE_HOME_METRICS = os.environ.get('OPAC_USE_HOME_METRICS', False)

# Acrônimo da coleção OPAC: 'spa' ou 'esp' por exemplo.
# -*- DEVE SER AJUSTADO NA INSTALAÇÃO -*-
OPAC_COLLECTION = os.environ.get('OPAC_COLLECTION', 'scl')


# Conta de email padrão para emails enviado do site - deve ser um email válido
DEFAULT_EMAIL = os.environ.get('OPAC_DEFAULT_EMAIL', 'scielo@scielo.org')

# Contas de email para receber mensagens de erros da interface.
_accounts_receive_errors = os.environ.get(
    'OPAC_EMAIL_ACCOUNTS_RECEIVE_ERRORS', None)
EMAIL_ACCOUNTS_RECEIVE_ERRORS = _accounts_receive_errors.split(
    ',') if _accounts_receive_errors else []

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
# Caminho absoluto da pasta que vai conter o arquivo sqlite
DATABASE_DIR = os.environ.get('OPAC_DATABASE_DIR', '/tmp')
DATABASE_PATH = '%s/%s' % (DATABASE_DIR, DATABASE_FILE)
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'OPAC_DATABASE_URI', 'sqlite:////%s' % DATABASE_PATH)
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

# migracao de paginas secundarias
DATA_PATH = os.path.join(PROJECT_PATH, '../../data')
# url do site anterior / indica quais links e imagens mudar de endereço
JOURNAL_PAGES_ORIGINAL_WEBSITE = os.environ.get(
    'ORIGINAL_WEBSITE') or ''
# local mapeado para obter as páginas secundárias (antigo `/revistas`)
JOURNAL_PAGES_SOURCE_PATH = os.environ.get(
    'OPAC_JOURNAL_PAGES_SOURCE_PATH', os.path.join(DATA_PATH, 'pages'))
# local mapeado para obter as images (antigo `/img/revistas`)
JOURNAL_IMAGES_SOURCE_PATH = os.environ.get(
    'OPAC_JOURNAL_IMAGES_SOURCE_PATH', os.path.join(DATA_PATH, 'img'))

# media files
DEFAULT_MEDIA_ROOT = os.path.abspath(os.path.join(PROJECT_PATH, 'media'))
MEDIA_ROOT = os.environ.get('OPAC_MEDIA_ROOT', DEFAULT_MEDIA_ROOT)
IMAGE_ROOT = os.path.join(MEDIA_ROOT, 'images')
FILE_ROOT = os.path.join(MEDIA_ROOT, 'files')
MEDIA_URL = os.environ.get('OPAC_MEDIA_URL', '/media')

# extensions
FILES_ALLOWED_EXTENSIONS = ('txt', 'pdf', 'csv', 'xls', 'doc',
                            'ppt', 'xlsx', 'docx', 'pptx', 'html', 'htm', 'svg')
IMAGES_ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif', 'webp')
IMAGES_ALLOWED_EXTENSIONS_RE = tuple(
    '*.' + ext for ext in IMAGES_ALLOWED_EXTENSIONS)
THUMBNAIL_HEIGHT = 100
THUMBNAIL_WIDTH = 100

# scielo.org
URL_SCIELO_ORG = os.environ.get('OPAC_URL_SCIELO_ORG', '//www.scielo.org')

SCIELO_ORG_URIS = {
    'journals_by_title': {
        'pt_BR': '/pt/periodicos/listar-por-ordem-alfabetica/',
        'en': '/en/journals/list-by-alphabetical-order/',
        'es': '/es/revistas/listar-por-orden-alfabetico/',
    },
    'journals_by_subject': {
        'pt_BR': '/pt/periodicos/listar-por-assunto/',
        'en': '/en/journals/list-by-subject-area/',
        'es': '/es/revistas/listar-por-tema',
    },
    'oai_and_rss': {
        'pt_BR': '/pt/sobre-o-scielo/acesso-via-oai-e-rss/',
        'en': '/en/about-scielo/access-via-oai-and-rss/',
        'es': '/es/sobre-el-scielo/acesso-via-oai-y-rss/',
    },
    'about_network': {
        'pt_BR': '/pt/sobre-o-scielo/',
        'en': '/en/about-scielo/',
        'es': '/es/sobre-el-scielo',
    },
    'contact': {
        'pt_BR': '/pt/sobre-o-scielo/contato/',
        'en': '/en/about-scielo/contact/',
        'es': '/es/sobre-el-scielo/contacto/',
    },
}

# scielo.org
URL_BLOG_SCIELO = os.environ.get('OPAC_URL_BLOG_SCIELO', '//blog.scielo.org')

# search scielo
URL_SEARCH = os.environ.get('OPAC_URL_SEARCH', '//search.scielo.org/')

# scielo em perspectiva press releases
URL_BLOG_PRESSRELEASE = os.environ.get(
    'OPAC_URL_BLOG_PRESSRELEASE ', '//pressreleases.scielo.org')

# analytics scielo
USE_METRICS = os.environ.get('OPAC_USE_METRICS', 'False') == 'True'
METRICS_URL = os.environ.get('OPAC_METRICS_URL', 'http://analytics.scielo.org')

# third-party metrics
USE_DIMENSIONS = os.environ.get('OPAC_USE_DIMENSIONS', 'False') == 'True'
DIMENSIONS_METRICS_URL = os.environ.get(
    'OPAC_DIMENSIONS_METRICS_URL',
    'https://badge.dimensions.ai/details/doi'
)
USE_PLUMX = os.environ.get('OPAC_USE_PLUMX', 'False') == 'True'
PLUMX_METRICS_URL = os.environ.get(
    'OPAC_PLUMX_METRICS_URL', 'https://plu.mx/scielo/a')
PLUMX_METRICS_JS = os.environ.get(
    'OPAC_PLUMX_METRICS_JS', '//cdn.plu.mx/widget-popup.js')


USE_ALTMETRIC = os.environ.get('OPAC_USE_ALTMETRIC', 'False') == 'True'
ALTMETRIC_METRICS_URL = os.environ.get(
    'OPAC_ALTMETRIC_METRICS_URL', 'https://www.altmetric.com/details.php')

USE_SCIENCEOPEN = os.environ.get('OPAC_USE_SCIENCEOPEN', 'False') == 'True'

USE_SCITE = os.environ.get('OPAC_USE_SCITE', 'False') == 'True'

SCITE_URL = os.environ.get('OPAC_SCITE_URL',
                           '//cdn.scite.ai/badge/scite-badge-latest.min.js')
SCITE_METRICS_URL = os.environ.get(
    'OPAC_SCITE_METRICS_URL', 'https://scite.ai/reports/')

ORCID_URL = os.environ.get(
    'OPAC_ORCID_URL', 'http://orcid.org/')

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
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get(
    'OPAC_TWITTER_ACCESS_TOKEN_SECRET', '')
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
OPAC_WTF_CSRF_SECRET_KEY = os.environ.get(
    'WTF_CSRF_SECRET_KEY', 'JGvNWiwBIq2Iig89LWbV')
READCUBE_ENABLED = os.environ.get('OPAC_READCUBE_ENABLED', 'False') == 'True'

# Conf de conexão com o SSM (pdfs e imagens)
SSM_SCHEME = os.environ.get('OPAC_SSM_SCHEME', 'https')
SSM_DOMAIN = os.environ.get('OPAC_SSM_DOMAIN', 'homolog.ssm.scielo.org')
SSM_PORT = os.environ.get('OPAC_SSM_PORT', '443')
SSM_MEDIA_PATH = os.environ.get('OPAC_SSM_MEDIA_PATH', '/media/assets/')
SSM_XML_URL_REWRITE = os.environ.get(
    'OPAC_SSM_XML_URL_REWRITE', 'True') == 'True'
SSM_ARTICLE_ASSETS_OR_RENDITIONS_URL_REWRITE = SSM_XML_URL_REWRITE

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

# session cookie settings:  z
OPAC_SCHEME = os.environ.get('OPAC_OPAC_SCHEME', 'https')
SERVER_NAME = os.environ.get('OPAC_SERVER_NAME', None)
OPAC_BASE_URI = "{scheme}://{domain}".format(
    scheme=OPAC_SCHEME,
    domain=SERVER_NAME)
SESSION_COOKIE_DOMAIN = os.environ.get('OPAC_SESSION_COOKIE_DOMAIN', SERVER_NAME)
SESSION_COOKIE_HTTPONLY = os.environ.get('OPAC_SESSION_COOKIE_HTTPONLY', 'True') == 'True'
SESSION_COOKIE_NAME = os.environ.get('OPAC_SESSION_COOKIE_NAME', 'opac_session')
SESSION_COOKIE_PATH = os.environ.get('OPAC_SESSION_COOKIE_PATH', None)
SESSION_COOKIE_SECURE = os.environ.get('OPAC_SESSION_COOKIE_SECURE', 'False') == 'True'
SESSION_REFRESH_EACH_REQUEST = os.environ.get('OPAC_SESSION_REFRESH_EACH_REQUEST', 'False') == 'True'


# Flask Caching:

CACHE_ENABLED = os.environ.get('OPAC_CACHE_ENABLED', 'False') == 'True'
CACHE_TYPE = os.environ.get('OPAC_CACHE_TYPE', 'redis')
CACHE_NO_NULL_WARNING = os.environ.get(
    'OPAC_CACHE_NO_NULL_WARNING', 'True') == 'True'
CACHE_DEFAULT_TIMEOUT = os.environ.get(
    'OPAC_CACHE_DEFAULT_TIMEOUT', 3600)  # segundos
CACHE_KEY_PREFIX = os.environ.get('OPAC_CACHE_KEY_PREFIX', 'opac_cache')
CACHE_REDIS_HOST = os.environ.get('OPAC_CACHE_REDIS_HOST', 'redis-cache')
CACHE_REDIS_PORT = os.environ.get('OPAC_CACHE_REDIS_PORT', 6379)
CACHE_REDIS_DB = os.environ.get('OPAC_CACHE_REDIS_DB', '0')
CACHE_REDIS_PASSWORD = os.environ.get('OPAC_CACHE_REDIS_PASSWORD', None)

# https://flask.palletsprojects.com/en/2.0.x/config/#SEND_FILE_MAX_AGE_DEFAULT
SEND_FILE_MAX_AGE_DEFAULT = os.environ.get(
    'OPAC_SEND_FILE_MAX_AGE_DEFAULT', 604800)

# https://werkzeug.palletsprojects.com/en/2.0.x/changes/?highlight=cache-control%20default%20#version-2-0-0
# https://github.com/pallets/werkzeug/issues/1882
CACHE_CONTROL_MAX_AGE_HEADER = os.environ.get(
    'OPAC_CACHE_CONTROL_MAX_AGE_HEADER', 604800)

# Pingdom Visitor Insights:
PINGDOM_VISITOR_INSIGHTS_JS_SRC = os.environ.get(
    'OPAC_PINGDOM_VISITOR_INSIGHTS_JS_SRC', None)

# Google Recaptcha
GOOGLE_RECAPTCHA_SECRET_KEY = os.environ.get(
    'OPAC_GOOGLE_RECAPTCHA_SECRET_KEY', "")
GOOGLE_RECAPTCHA_URL = os.environ.get(
    'OPAC_GOOGLE_RECAPTCHA_URL', "//www.google.com/recaptcha/api.js")
GOOGLE_VERIFY_RECAPTCHA_URL = os.environ.get(
    'OPAC_GOOGLE_VERIFY_RECAPTCHA_URL', "https://www.google.com/recaptcha/api/siteverify")
GOOGLE_VERIFY_RECAPTCHA_KEY = os.environ.get(
    'OPAC_GOOGLE_VERIFY_RECAPTCHA_KEY', "")

SCIMAGO_URL = os.environ.get(
    'SCIMAGO_URL',
    'https://www.scimagojr.com/journalsearch.php?tip=sid&clean=0&q=')
SCIMAGO_ENABLED = os.environ.get('SCIMAGO_ENABLED', 'True') == 'True'

# SCImago Institutions Ranking(IR)
SCIMAGO_URL_IR = os.environ.get('OPAC_SCIMAGO_URL_IR', 'https://www.scimagoir.com/')

# Audit Log Email notifications:
AUDIT_LOG_NOTIFICATION_ENABLED = os.environ.get(
    'OPAC_AUDIT_LOG_NOTIFICATION_ENABLED', 'True') == 'True'
_audit_log_notification_recipients = os.environ.get(
    'OPAC_AUDIT_LOG_NOTIFICATION_RECIPIENTS', None)
AUDIT_LOG_NOTIFICATION_RECIPIENTS = _audit_log_notification_recipients.split(
    ',') if _audit_log_notification_recipients else []


# RQ REDIS CONNECTION
REDIS_HOST = os.environ.get('OPAC_RQ_REDIS_HOST', CACHE_REDIS_HOST)
REDIS_PORT = int(os.environ.get('OPAC_RQ_REDIS_PORT', CACHE_REDIS_PORT))
REDIS_PASSWORD = os.environ.get('OPAC_RQ_REDIS_PASSWORD', None)
RQ_REDIS_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
RQ_REDIS_SETTINGS = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'password': REDIS_PASSWORD,
}
MAILING_CRON_STRING = os.environ.get(
    'OPAC_MAILING_CRON_STRING', '0 7 * * *')
DEFAULT_SCHEDULER_TIMEOUT = int(
    os.environ.get('OPAC_DEFAULT_SCHEDULER_TIMEOUT', 1000))

# MATH JAX
DEFAULT_MATHJAX_CDN_URL = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_SVG"

MATHJAX_CDN_URL = os.environ.get(
    'OPAC_MATHJAX_CDN_URL', DEFAULT_MATHJAX_CDN_URL)


# RELATED ARTICLES
OPAC_GOOGLE_SCHOLAR_LINK = os.environ.get(
    'OPAC_GOOGLE_SCHOLAR', "https://scholar.google.com/scholar?q=")
OPAC_GOOGLE_LINK = os.environ.get(
    'OPAC_GOOGLE', "https://www.google.com/search?q=")


# COOKIE POLICY
COOKIE_POLICY_ENABLED = os.environ.get(
    'OPAC_COOKIE_POLICY_ENABLED', 'True') == 'True'
COOKIE_POLICY_URL = os.environ.get(
    'OPAC_COOKIE_POLICY_URL', "https://static.scielo.org/js/cookiePolicy.min.js")

# APM Config
APM_ENABLED = os.environ.get('OPAC_APM_ENABLED', 'False') == 'True'
APM_SERVER_URL = os.environ.get('OPAC_APM_SERVER_URL')
APM_SERVICE_NAME = os.environ.get('OPAC_APM_SERVICE_NAME', 'Website')
APM_SECRET_TOKEN = os.environ.get('OPAC_APM_SECRET_TOKEN')
APM_ENVIRONMENT = os.environ.get('OPAC_APM_ENVIRONMENT')
APM_SERVICE_VERSION = os.environ.get('OPAC_APM_SERVICE_VERSION')
APM_FILTER_EXCEPTION_TYPES = os.environ.get("OPAC_APM_FILTER_EXCEPTION_TYPES")
APM_TRANSACTIONS_IGNORE_PATTERNS = os.environ.get(
    "OPAC_APM_TRANSACTIONS_IGNORE_PATTERNS")
APM_SERVER_TIMEOUT = os.environ.get("OPAC_APM_SERVER_TIMEOUT")
APM_HOSTNAME = os.environ.get("OPAC_APM_HOSTNAME")
APM_COLLECT_LOCAL_VARIABLES = os.environ.get(
    "OPAC_APM_COLLECT_LOCAL_VARIABLES")
APM_LOCAL_VAR_MAX_LENGTH = os.environ.get("OPAC_APM_LOCAL_VAR_MAX_LENGTH")
APM_CAPTURE_BODY = os.environ.get("OPAC_APM_CAPTURE_BODY")
APM_CAPTURE_HEADERS = os.environ.get("OPAC_APM_CAPTURE_HEADERS", True)
APM_TRANSACTION_MAX_SPANS = os.environ.get("OPAC_APM_TRANSACTION_MAX_SPANS")
APM_STACK_TRACE_LIMIT = os.environ.get("OPAC_APM_STACK_TRACE_LIMIT")
APM_DEBUG = os.environ.get("OPAC_APM_DEBUG", False)
APM_DISABLE_SEND = os.environ.get("OPAC_APM_DISABLE_SEND", False)
APM_INSTRUMENT = os.environ.get("OPAC_APM_INSTRUMENT", True)
APM_VERIFY_SERVER_CERT = os.environ.get(
    "OPAC_APM_APM_VERIFY_SERVER_CERT", True)

# Caso queira apresentar na home do website que o atual tem versão anterior
PREVIOUS_WEBSITE_URI = os.environ.get("PREVIOUS_WEBSITE_URI", '')

# Caso queira apresentar na home do website qualquer mensagem de texto
ALERT_MSG_PT = os.environ.get("ALERT_MSG_PT", '')
ALERT_MSG_EN = os.environ.get("ALERT_MSG_EN", '')
ALERT_MSG_ES = os.environ.get("ALERT_MSG_ES", '')
ALERT_MSG = bool(ALERT_MSG_PT or ALERT_MSG_EN or ALERT_MSG_ES)


# Google Meta tags
FORCE_USE_HTTPS_GOOGLE_TAGS = os.environ.get(
    "OPAC_FORCE_USE_HTTPS_GOOGLE_TAGS", True)

# Filtro por seção no TOC
FILTER_SECTION_ENABLE = os.environ.get(
    "OPAC_FILTER_SECTION_ENABLE", False)

# Linguagens suportados
ACCESSIBILITY_BY_LANGUAGE = {
    'pt_BR': os.environ.get("ACCESSIBILITY_FORM_PT", 'https://forms.gle/2Vpt2z26uGqHA7yy5'),
    'en': os.environ.get("ACCESSIBILITY_FORM_EN", 'https://forms.gle/qHwovmddXdZRDxjm7'),
    'es': os.environ.get("ACCESSIBILITY_FORM_ES", 'https://forms.gle/XZuJurSVMBp4E64j6'),
}

# Common Style List
COMMON_STYLE_LIST = os.environ.get("OPAC_COMMON_STYLE_LIST", os.path.abspath(
    os.path.join(PROJECT_PATH, 'media/csl_styles.json')))

# Citation Export Format
CITATION_EXPORT_FORMATS = {"bib": "BibTex",
                           "ris": "Reference Manager"}
