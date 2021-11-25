
### SciELO - On-line Public Access Catalog


### Instalação e configuração


Em nossa `wiki <https://github.com/scieloorg/opac/wiki>`_ você tem as diferentes guias de instalação e configuração para diferentes ambientes:

- `De desenvolvimento <https://github.com/scieloorg/opac/wiki/Configura%C3%A7%C3%A3o-e-instala%C3%A7%C3%A3o>`_
- `De produção com Gunicorn/Nginx/Supervisor em CentOS <https://github.com/scieloorg/opac/wiki/Configura%C3%A7%C3%A3o-e-instala%C3%A7%C3%A3o-%28ambiente-de-produ%C3%A7%C3%A3o%29-Gunicorn>`_
- `De produção com Chaussette/Nginx/Circus em CentOS <https://github.com/scieloorg/opac/wiki/Configura%C3%A7%C3%A3o-e-instala%C3%A7%C3%A3o-%28ambiente-de-produ%C3%A7%C3%A3o%29-Gunicorn>`_



### Guia de configuração do site


Pode acessar `nossa wiki <https://github.com/scieloorg/opac/wiki/Configura%C3%A7%C3%A3o-padr%C3%A3o-e-vari%C3%A1veis-de-ambiente>`_ para ter uma guia completa e como ajustar a configuração a partir de um arquivo de configuração em cada instância ou utilizando variáveis de ambiente.


Caso queira apresentar na home do website o link para a versão anterior do site

PREVIOUS_WEBSITE_URI=https://old.scielo.br


Caso queira apresentar na home do website qualquer mensagem de texto

ALERT_MSG_PT=Novo portal pode conter incorreções
ALERT_MSG_EN=New portal may contain inaccuracies
ALERT_MSG_ES=Nuevo portal puede contener incorrecciones



### Como executar os tests



- Para rodar os tests de unidade, pode executar: ``make test``
- Para ter o relatório de coverage deve executar: ``make test_coverage``



### Arquivos: Dockerfile* e docker-compose*.yml



- **Dockerfile**: contém as definições para construir a imagem pronta para instalar em **produção**
- **Dockerfile-dev**: contém as definições para construir a imagem pronta para instalar em **desenvolvimento**

- **docker-compose.yml**: contém as definições para iniciar todos os containers necessários para rodar em **produção**
- **docker-compose-build.yml**: contém as definições para construir as imagems e iniciar todos os containers necessários para rodar no **Travis/CI**
- **docker-compose-dev.yml**: contém as definições para iniciar todos os containers necessários para rodar em **desenvolvimento**



### Variáveis de ambiente
|        Variável       	| Valor padrão 	| Valores possíveis 	| Última avaliação 	| Observações 	|
|:---------------------	|:------------	|:-----------------	|:----------------	|:-----------	|
| OPAC_USE_HOME_METRICS 	|       False   |         True/False 	|        21/11/2021 |     ativa/desativa a apresentação dos dados de métricas da coleção (default: False), o padrão é não apresentar        	|
|          OPAC_DEBUG_MODE  |     False    	|  True/False         	|        21/11/2021 |       ativa/desativa o modo Debug da app, deve estar desativado em produção! (default: False)      	|
|        OPAC_SECRET_KEY  	|       secr3t-k3y    	|           '123523445werw45345'        	|       21/11/2021           	|       chave aleatória necessária para segurança nos formulario da app.|
|        OPAC_COLLECTION  	|       scl    	|           scl, spa, mex, cub, entre outros acrônimos válidos        	|       21/11/2021           	|       acrônimo da coleção do opac|
|        OPAC_DEFAULT_EMAIL  	|       scielo@scielo.org    	|           admin@scielo.org, scielo@scielo.org        	|       21/11/2021           	|       conta de email para envio de mensagens desde o site|
|        OPAC_MAIL_SERVER  	|       localhost    	|           localhost, 127.0.0.1, 0.0.0.0        	|       21/11/2021           	|       host do servidor de emails|
|        OPAC_MAIL_PORT  	|       1025    	|           25, 485, 1025         	|       21/11/2021           	|       porta do servidor de emails|
|        OPAC_MAIL_USE_TLS  	|       False    	|           True/False         	|       21/11/2021           	|       ativa/desativa envio de email com TLS|
|        OPAC_MAIL_USE_SSL  	|       False    	|           True/False         	|       21/11/2021           	|       ativa/desativa envio de email com SSL|
|        OPAC_MONGODB_NAME  	|       opac    	|           opac, opac_spa, opac_mex         	|       21/11/2021           	|       nome do banco|
|        OPAC_MONGODB_HOST  	|       localhost    	|           localhost, 127.0.0.1, 0.0.0.0         	|       21/11/2021           	|       host do banco|
|        OPAC_MONGODB_PORT  	|       27017    	|           27017, 27018, 27019         	|       21/11/2021           	|       porta do banco|
|        OPAC_MONGODB_USER  	|       None    	|           opac_user         	|       21/11/2021           	|       usuário para acessar o banco, essa variável é opcional|
|        OPAC_MONGODB_PASS  	|        None   	|           12345         	|       21/11/2021           	|       password para acessar o banco|
|        OPAC_DATABASE_FILE  	|        opac.sqlite   	|           opac_spa.sqlite         	|       21/11/2021           	|       nome do arquivo (sqlite)|
|        OPAC_DATABASE_DIR  	|        /tmp   	|           /app/database/, /app, /tmp         	|       21/11/2021           	|       pasta aonde fica o banco (sqlite)|
|        OPAC_DATABASE_DIR  	|       sqlite:////tmp/opac.sqlite    	|           sqlite:////tmp/opac.sqlite         	|       21/11/2021           	|       URI do banco sql opcional|
|        GA_TRACKING_CODE  	|         G-MKLVK7B5B4  	|         G-MKLVK7B4B6           	|       21/11/2021           	|       código de google analytics (acesse https://goo.gl/HE77SO para resgatar seu código)|
|        OPAC_MEDIA_ROOT  	|         /[repo dir]/opac/opac/webapp/media/  	|         /[repo dir]/opac/opac/webapp/media/           	|       21/11/2021           	|       path absoluto da pasta que vai armazenar as imagens subidas pelos usuários pelo admin.|
|        OPAC_MEDIA_URL  	|         /media/  	|         /media/            	|       21/11/2021           	|       URL para servir as imagens.|
|        FILES_ALLOWED_EXTENSIONS  	|        ('txt', 'pdf', 'csv', 'xls', 'doc', 'ppt', 'xlsx', 'docx', 'pptx', 'html', 'htm')   	|            ('txt', 'pdf', 'csv', 'xls', 'doc', 'ppt', 'xlsx', 'docx', 'pptx', 'html', 'htm')         	|       21/11/2021           	|       conjunto de extensões dos arquivos permitidos para upload|
|        IMAGES_ALLOWED_EXTENSIONS  	|         ('png', 'jpg', 'jpeg', 'gif', 'webp')  	|         ('png', 'jpg', 'jpeg', 'gif', 'webp')           	|       21/11/2021           	|       extensão imagens permitidas para upload|
|        THUMBNAIL_HEIGHT  	|         100  	|         100, 200,            	|       21/11/2021           	|       altura do thumbnail|
|        THUMBNAIL_WIDTH  	|         100  	|         100, 200,            	|       21/11/2021           	|       largura do thumbnail|
|        OPAC_TWITTER_CONSUMER_KEY  	|         consum3r-k3y  	|           consum3r-k3y          	|       21/11/2021           	|       Twitter consumer key|
|        OPAC_TWITTER_CONSUMER_SECRET  	|         consum3r-secr3t  	|         consum3r-secr3t            	|       21/11/2021           	|       Twitter consumer secret|
|        OPAC_TWITTER_ACCESS_TOKEN  	|         acc3ss-tok3n-secr3t  	|         acc3ss-tok3n-secr3t            	|       21/11/2021           	|       Twitter access token|
|        OPAC_TWITTER_ACCESS_TOKEN_SECRET  	|         acc3ss-tok3n-secr3t  	|         acc3ss-tok3n-secr3t            	|       21/11/2021           	|       Twitter access token|
|        OPAC_TWITTER_SCREEN_NAME  	|         RedeSciELO  	|         RedeSciELO, SciELO, Scielo Espanha            	|       21/11/2021           	|       Twitter screen name |
|        OPAC_USE_METRICS  	|         False  	|         True/False            	|       21/11/2021           	|       ativa/desativa a integração com o SciELO Analytics. Se sim, definir como 'True' |
|        OPAC_METRICS_URL  	|         http://analytics.scielo.org  	|         http://analytics.scielo.org            	|       21/11/2021           	|       URL para SciELO Analytics |
|        OPAC_USE_DIMENSIONS  	|         False  	|         True/False            	|       21/11/2021           	|       ativa/desativa a integração com o Dimensions. Se sim, definir como 'True' |
|        OPAC_DIMENSIONS_METRICS_URL  	|         https://badge.dimensions.ai/details/doi  	|         https://badge.dimensions.ai/details/doi            	|       21/11/2021           	|       URL para o Dimensions |
|        OPAC_USE_PLUMX  	|         False  	|         True/False            	|       21/11/2021           	|       ativa/desativa a integração com o PlumX. Se sim, definir como 'True' |
|        OPAC_PLUMX_METRICS_URL  	|         //cdn.plu.mx/widget-popup.js  	|         //cdn.plu.mx/widget-popup.js            	|       21/11/2021           	|       URL para o PlumX  |
|        OPAC_USE_SCIENCEOPEN  	|         False  	|         True/False            	|       21/11/2021           	|       ativa/desativa a integração de métricas com o ScienceOpen. Se sim, definir como 'True'  |
|        OPAC_USE_SCITE  	|         False  	|         True/False            	|       21/11/2021           	|       ativa/desativa a integração de métricas com _SCITE. Se sim, definir como 'True'   |
|        OPAC_SCITE_URL  	|         https://cdn.scite.ai/badge/scite-badge-latest.min.js  	|         https://cdn.scite.ai/badge/scite-badge-latest.min.js            	|       21/11/2021           	|       URL para o SCITE_ JS  |
|        OPAC_SCITE_METRICS_URL  	|         https://scite.ai/reports/  	|         https://scite.ai/reports/            	|       21/11/2021           	|       URL para o Scite_   |
|        LOCAL_ZONE  	|         'America/Sao_Paulo'  	|         'America/Sao_Paulo'            	|       21/11/2021           	|       Localização para data   |
|        OPAC_USE_SENTRY  	|         False  	|         True/False            	|       21/11/2021           	|       ativa/desativa a integração com Sentry, se sim definir como: 'True'   |
|        OPAC_SENTRY_DSN  	|         None  	|         DSN do Sentry            	|       21/11/2021           	|       DSN definido pelo sentry para este projeto. Utilizado só se OPAC_USE_SENTRY == True   |
|        OPAC_BUILD_DATE  	|         None  	|         05/11/2002, 09/02/2009            	|       21/11/2021           	|       data de build. definida em tempo de construção da imagem   |
|        OPAC_VCS_REF  	|         None  	|         None            	|       21/11/2021           	|       commit do código. definida pelo travis em tempo de construção da imagem.   |
|        OPAC_WEBAPP_VERSION  	|         None  	|         3.44.5,3.43.2            	|       21/11/2021           	|       'versão do OPAC WEBAPP'. definida pelo travis em tempo de construção da imagem. definida pelo travis em tempo de construção da imagem.   |
|        OPAC_WTF_CSRF_ENABLED  	|         True  	|         True/False            	|       21/11/2021           	|        ativa/desativa o recurso de CSRF   |
|        OPAC_WTF_CSRF_SECRET_KEY  	|         JGvNWiwBIq2Iig89LWbV  	|                     	|       21/11/2021           	|        chave para segurança nos formulários WTF.   |
|        READCUBE_ENABLED  	|         False  	|          True/False           	|       21/11/2021           	|        ativa/desativa a exibição do link para o ReadCube, se sim definir como: 'True'    |
|
|        OPAC_SSM_SCHEME  	|         https  	|          http/https           	|       21/11/2021           	|        Protocolo de conexão com SSM. Opções: 'http' ou 'https' - (default: 'https')    |
|        OPAC_SSM_DOMAIN  	|         ssm.scielo.org  	|          ssm.scielo.org dam.doamin.suffix           	|       21/11/2021           	|        Dominio/FQDN da conexão com SSM. Ex: 'homolog.ssm.scielo.org    |
|        OPAC_SSM_PORT  	|         80  	|          80, 8000           	|       21/11/2021           	|        Dominio/FQDN da conexão com SSM.    |
|        OPAC_SSM_MEDIA_PATH  	|         '/media/assets/'  	|          '/media/assets/', '/media/files/'           	|       21/11/2021           	|        Path da pasta media do assests no SSM.    |
|        OPAC_SSM_XML_URL_REWRITE  	|         True  	|          True/False            	|       21/11/2021           	|        Troca o scheme + authority da URL armazenada em Article.xml por `OPAC_SSM_SCHEME + '://' + OPAC_SSM_DOMAIN + ':' + OPAC_SSM_PORT`.    |
|        OPAC_SERVER_NAME  	|         None  	|          www.scielo.br, www.scielosp.org            	|       21/11/2021           	|        Nome: IP do servidor    |
|        OPAC_SESSION_COOKIE_DOMAIN  	|         OPAC_SERVER_NAME  	|          www.scielo.br, www.scielosp.org            	|       21/11/2021           	|        O dominio para a cookie da sessão     |
|        OPAC_SESSION_COOKIE_HTTPONLY  	|         True  	|          True/False            	|       21/11/2021           	|        Seta a flag: httponly da cookie.     |
|        OPAC_SESSION_COOKIE_NAME  	|         opac_session  	|          opac_session            	|       21/11/2021           	|        nome da cookie de sessão     |
|        OPAC_SESSION_COOKIE_PATH  	|         None  	|          '/'            	|       21/11/2021           	|        path para a cookie de sessão     |
|        OPAC_SESSION_COOKIE_SECURE  	|         False  	|          True/False            	|       21/11/2021           	|        define se a cookie de sessão deve ser marcada como segura     |
|        OPAC_SESSION_REFRESH_EACH_REQUEST  	|         False  	|          True/False            	|       21/11/2021           	|        Fazer refresh da cookie em cada request?     |
|        OPAC_CACHE_ENABLED  	|         True  	|          True/False            	|       21/11/2021           	|         ativa/desativa o cache com redis    |
|        OPAC_CACHE_TYPE  	|         redis  	|          redi, null            	|       21/11/2021           	|         O tipo de backend do cache: 'null', 'redis', outros    |
|        OPAC_CACHE_NO_NULL_WARNING  	|         True  	|          True/False            	|       21/11/2021           	|         ativa/desativa exibição de warnings quando o CACHE_TYPE é 'null'    |
|        OPAC_CACHE_DEFAULT_TIMEOUT  	|         3600  	|          3600, 5200            	|       21/11/2021           	|         tempo de vida dos objetos no cache. Tempo medido em segundos     |
|        OPAC_CACHE_KEY_PREFIX  	|         opac_cache  	|          opac_cache, opac, cache            	|       21/11/2021           	|         prefixo da chave de cache     |
|        OPAC_CACHE_REDIS_HOST  	|         redis-cache  	|          redis-cache            	|       21/11/2021           	|         host do servidor redis que vai ser usado no cache.     |
|        OPAC_CACHE_REDIS_PORT  	|         6379  	|          6379            	|       21/11/2021           	|         porta do servidor redis que vai ser usado no cache.     |
|        OPAC_CACHE_REDIS_DB  	|         0  	|          inteiro >= 0            	|       21/11/2021           	|         nome de db do servidor redis que vai ser usado no cache     |
|        OPAC_CACHE_REDIS_PASSWORD  	|         None  	|          senha            	|       21/11/2021           	|         senha do servidor redis que vai ser usado no cache.    |
|        OPAC_PINGDOM_VISITOR_INSIGHTS_JS_SRC  	|         None  	|          //rum-static.pingdom.net/pa-XXXXXXXXX.js            	|       21/11/2021           	|         URL do JS para utilizar o Pingdom visitor insights (ex: `//rum-static.pingdom.net/pa-XXXXXXXXX.js`)    |
|        OPAC_GOOGLE_RECAPTCHA_SECRET_KEY  	|         chave do google  	|                      	|       21/11/2021           	|         Chave do site    |
|        OPAC_GOOGLE_VERIFY_RECAPTCHA_KEY  	|         chave do secreta do google  	|         6LcMGeoUAAAAALMHmu9872DeufdBVvF2ZRBzEwyCn7Jd             	|       21/11/2021           	|         Chave secreta do parceiro    |
|        OPAC_GOOGLE_RECAPTCHA_URL  	|         chave do secreta do google  	|                      	|       21/11/2021           	|         URL do JavaScript Google reCAPTCHA    |
|        OPAC_GOOGLE_VERIFY_RECAPTCHA_URL  	|         https://www.google.com/recaptcha/api/siteverify  	|      https://www.google.com/recaptcha/api/siteverify                	|       21/11/2021           	|      URL de verificação do google      |
|        OPAC_EMAIL_ACCOUNTS_RECEIVE_ERRORS  	|         None  	|      webmaster@scielo.org                	|       21/11/2021           	|      Contas de email para receber mensagens de erros da interface      |
|        OPAC_AUDIT_LOG_NOTIFICATION_ENABLED  	|         True  	|     True/False                 	|       21/11/2021           	|      ativa/desativa envio de notificações via email do relatorio de auditoria      |
|        OPAC_AUDIT_LOG_NOTIFICATION_ENABLED  	|         True  	|     True/False                 	|       21/11/2021           	|      ativa/desativa envio de notificações via email do relatorio de auditoria      |
|        OPAC_AUDIT_LOG_NOTIFICATION_RECIPIENTS  	|         scielo@scielo.org  	|     emails                 	|       21/11/2021           	|      lista de email que devem receber o emails com relatorio de auditoria      |
|        OPAC_RQ_REDIS_HOST  	|         localhost  	|          localhost, 127.0.0.1, 0.0.0.0            	|       21/11/2021           	|      localhost do servidor de Redis (pode ser o mesmo server do Cache)      |
|        OPAC_RQ_REDIS_PORT  	|         None  	|          None           	|       21/11/2021           	|      porta do servidor de Redis (pode ser o mesmo server do Cache)      |
|        OPAC_RQ_REDIS_PASSWORD  	|         None  	|          None           	|       21/11/2021           	|      senha do servidor de Redis (pode ser o mesmo server do Cache)      |
|        OPAC_MAILING_CRON_STRING  	|         None  	|          None           	|       21/11/2021           	|      valor de cron padrão para o envio de emails      |
|        OPAC_DEFAULT_SCHEDULER_TIMEOUT  	|         1000  	|          None           	|       21/11/2021           	|      timeout do screduler cron.      |
|        OPAC_MATHJAX_CDN_URL  	|         https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-AMS-MML_HTMLorMML  	|          https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-AMS-MML_HTMLorMML           	|       21/11/2021           	|      string com a URL do mathjax padrão      |
|        URL_SCIELO_ORG  	|         //www.scielo.org  	|          //www.scielo.org           	|       21/11/2021           	|      URL para o SciELO.org      |
|        URL_BLOG_SCIELO  	|         //blog.scielo.org  	|          //blog.scielo.org           	|       21/11/2021           	|      URL para o Blog SciELO em Perspectiva      |
|        URL_SEARCH  	|         //search.scielo.org/  	|          //search.scielo.org/           	|       21/11/2021           	|      URL para o Search SciELO      |
|        URL_BLOG_PRESSRELEASE  	|         //pressreleases.scielo.org  	|          //pressreleases.scielo.org           	|       21/11/2021           	|      URL para o Blog SciELO em Perspectiva Press releases      |
|        OPAC_COOKIE_POLICY_ENABLED  	|         https://static.scielo.org/js/cookiePolicy.min.js  	|          ttps://static.scielo.org/js/cookiePolicy.min.js           	|       21/11/2021           	|      ativa/desativa o javascript de política de cookie, se sim definir como: 'True' caso contrário 'False' |
|        OPAC_ORCID_URL  	|         http://orcid.org/  	|          http://orcid.org/           	|       21/11/2021           	|      URL do ORCID.)|
|        OPAC_FORCE_USE_HTTPS_GOOGLE_TAGS  	|         True 	|          True/False           	|       21/11/2021           	|      Força o uso de https nas URLs para do site do OPAC nas tags do google|
|        OPAC_FILTER_SECTION_ENABLE  	|         False  	|          True/False           	|       21/11/2021           	|      ativa/desativa o filtro por seção na página do issue|




### Instalação utilizando Docker para desenvolvimento



Para executar o ambiente (de desenvolvimento) com Docker, utilizando as definições do arquivo **Dockerfile-dev** e **docker-compose.yml-dev** na raiz do projeto.
Simplesmente executar:

1. executar: ``make dev_compose_build`` para construir a imagem do OPAC.
2. executar: ``make dev_compose_up``  para rodar os containers.
3. acessar pelo browser: http://localhost ou no caso de utilizar OSx trocar localhost pela IP da maquina default (ver na saída do comando: ``docker-machine ip``)
4. para inspecionar os logs, executar: ``make dev_compose_logs``
5. para interromper os containers, executar: ``make dev_compose_stop``
6. para abrir uma terminal dentro do container, executar: ``make dev_compose_exec_shell_webapp``


### Fixtures

Procedimento para popular a instância de desenvolvimento a partir de fixtures disponibilizadas pelo SciELO.

1. Para execução dos procedimentos que adicionam dados no banco é necessário que o ambiente de desenvolvimento do OPAC esteja rodando ``make dev_compose_up``
2. Baixar a fixture de desenvolvimento, execute: ``wget https://minio.scielo.br/dev/fixtures/opac_br.zip``
3. Extraia o conteúdo, execute: ``unzip opac_br.zip``
4. Repare que uma pasta chamada opac_br foi criada e dentro dela há arquivos .bson, .json, .sqlite e outra pasta chamada media que contém os ativos dos periódicos e da coleção.
5. Acesse a pasta **opac_br**, execute: ``cd opac_br``
6. Utilizando **mongorestore** realize a recuperação do banco de dados apontando para o endereço que está rodando o seu mongo local, exemplo: ``mongorestore --host=localhost --port=27017 --db=opac --dir .``
7. Realize a cópia da pasta **media** para a pasta data. A pasta data está na raiz deste repositório e é, por padrão, mapeada à aplicação OPAC.
8. Realize a cópia da pasta **opac.sqlite** para a pasta data. A pasta data está na raiz deste repositório e é, por padrão, mapeada à aplicação OPAC.
9. Os seguintes parâmetros devem está configurados no arquivo ``docker-compose-dev.yml``:

- OPAC_SSM_DOMAIN=minio.scielo.br
- OPAC_SSM_PORT=443
- OPAC_SSM_SCHEME=https
- OPAC_SSM_XML_URL_REWRITE=False

10. Para ambiente utilizando **Docker** é necessário reiniciar os containers: ``make dev_compose_stop`` && ``make dev_compose_up``

Caso não tenha o **mongorestore** localmente é necessário instalar a aplicação **MONGODB DATABASE TOOLS**: https://docs.mongodb.com/database-tools/installation/installation/

Para utilizar o ambiente de desenvolvimento com o banco de dados populado a partir dos passos indicados nestas instruções, é necessário estar conectado à **VPN da SciELO**. Caso não esteja conectado, as páginas de artigos estarão indisponíveis.

A área administrativa possui um usuário cadastrado. Acesse http://0.0.0.0:8000/admin com as seguintes credenciais:

**Usuário:** admin@admin.com

**Senha:** admin

Caso queira alterar para um mongodb local do hospedeiro, é necessário alterar o parâmetro: ``OPAC_MONGODB_HOST`` no ``docker-compose-dev.yml``.


### Reportar problemas, ou solicitar mudanças


Para reportar problemas, bugs, ou simplesmente solicitar alguma nova funcionalidade, pode `criar um ticket <https://github.com/scieloorg/opac/issues>`_ com seus pedidos.
