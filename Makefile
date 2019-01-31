default: test

COMPOSE_FILE_DEV = docker-compose-dev.yml
COMPOSE_FILE_BUILD = docker-compose-build.yml

export OPAC_BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
export OPAC_VCS_REF=$(strip $(shell git rev-parse --short HEAD))
export OPAC_WEBAPP_VERSION=$(strip $(shell cat VERSION))

ifndef OPAC_STATIC_REPO_PATH
    OPAC_STATIC_REPO_PATH=$(abspath $(dir $CURDIR/../../../bitbucket.org/portal-scielo/))
else
    @echo "$$OPAC_STATIC_REPO_PATH já foi definida previamente: $(OPAC_STATIC_REPO_PATH)"
endif

opac_version:
	@echo "Version file: " $(OPAC_WEBAPP_VERSION)

vcs_ref:
	@echo "Latest commit: " $(OPAC_VCS_REF)

build_date:
	@echo "Build date: " $(OPAC_BUILD_DATE)

############################################
## atalhos docker-compose desenvolvimento ##
############################################

dev_compose_build:
	@docker-compose -f $(COMPOSE_FILE_DEV) build

dev_compose_up:
	@docker-compose -f $(COMPOSE_FILE_DEV) up -d

dev_compose_logs:
	@docker-compose -f $(COMPOSE_FILE_DEV) logs -f $(SERVICE)

dev_compose_stop:
	@docker-compose -f $(COMPOSE_FILE_DEV) stop

dev_compose_ps:
	@docker-compose -f $(COMPOSE_FILE_DEV) ps

dev_compose_rm:
	@docker-compose -f $(COMPOSE_FILE_DEV) rm -f

dev_compose_exec_shell_webapp:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec opac_webapp sh

dev_compose_make_test:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec opac_webapp make test

dev_compose_invalidate_cache:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec opac_webapp make invalidate_cache

dev_compose_invalidate_cache_forced:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec opac_webapp make invalidate_cache_forced


#####################################################
## atalhos docker-compose build e testes no traivs ##
#####################################################

travis_compose_build:
	@echo "[Travis Build] opac version: " $(OPAC_WEBAPP_VERSION)
	@echo "[Travis Build] lates commit: " $(OPAC_VCS_REF)
	@echo "[Travis Build] build date: " $(OPAC_BUILD_DATE)
	@echo "[Travis Build] compose file: " $(COMPOSE_FILE_BUILD)
	@docker-compose -f $(COMPOSE_FILE_BUILD) build

travis_compose_up:
	@docker-compose -f $(COMPOSE_FILE_BUILD) up -d

travis_compose_make_test:
	@docker-compose -f $(COMPOSE_FILE_BUILD) exec opac_webapp make test

travis_run_audit:
	@docker run \
	-it --net host --pid host \
	--cap-add audit_control \
	-v /var/lib:/var/lib \
  	-v /var/run/docker.sock:/var/run/docker.sock \
  	-v /usr/lib/systemd:/usr/lib/systemd \
  	-v /etc:/etc \
  	--label docker_bench_security \
  	docker/docker-bench-security

###########################################################
## atalhos docker-compose build e push para o Docker Hub ##
###########################################################

release_docker_build:
	@echo "[Building] Release version: " $(OPAC_WEBAPP_VERSION)
	@echo "[Building] Latest commit: " $(OPAC_VCS_REF)
	@echo "[Building] Build date: " $(OPAC_BUILD_DATE)
	@echo "[Building] Image full tag: $(TRAVIS_REPO_SLUG):$(COMMIT)"
	@docker build \
	-t $(TRAVIS_REPO_SLUG):$(COMMIT) \
	--build-arg OPAC_BUILD_DATE=$(OPAC_BUILD_DATE) \
	--build-arg OPAC_VCS_REF=$(OPAC_VCS_REF) \
	--build-arg OPAC_WEBAPP_VERSION=$(OPAC_WEBAPP_VERSION) .

release_docker_tag:
	@echo "[Tagging] Target image -> $(TRAVIS_REPO_SLUG):$(COMMIT)"
	@echo "[Tagging] Image name:latest -> $(TRAVIS_REPO_SLUG):latest"
	@docker tag $(TRAVIS_REPO_SLUG):$(COMMIT) $(TRAVIS_REPO_SLUG):latest
	@echo "[Tagging] Image name:latest -> $(TRAVIS_REPO_SLUG):travis-$(TRAVIS_BUILD_NUMBER)"
	@docker tag $(TRAVIS_REPO_SLUG):$(COMMIT) $(TRAVIS_REPO_SLUG):travis-$(TRAVIS_BUILD_NUMBER)

release_docker_push:
	@echo "[Pushing] pushing image: $(TRAVIS_REPO_SLUG)"
	@docker push $(TRAVIS_REPO_SLUG)
	@echo "[Pushing] push $(TRAVIS_REPO_SLUG) done!"

#########
## i18n #
#########

# IMPORTANTE: Seguir os seguintes passos para atualização dos .pot e po:
#
# 1. make make_message (Varre todos os arquivo [.html, .py, .txt, ...] buscando por tags de tradução)
# 2. make update_catalog (Atualizar todos os com .po a apartir do .pot)
# 3. acessar a ferramenta de tradução colaborativa Transifex(https://www.transifex.com) atualizar o arquivo .pot
# 4. utilizando a interface do Transifex é possível realizar as traduções
# 5. após finalizar as traduções realize o download manual dos arquivo traduzidos para suas correspondentes pasta ```opac/webapp/translations/{LANG}/LC_MESSAGES```
# 6. make compile_messages para gerar os arquivo .mo
# 7. realize a atualização no repositório de códigos.

# Faz um scan em toda a opac/webapp buscando strings traduzíveis e o resultado fica em opac/webapp/translations/messages.pot
make_messages:
	pybabel extract -F opac/webapp/config/babel.cfg -k lazy_gettext -k __ -o opac/webapp/translations/messages.pot .

# cria o catalogo para o idioma definido pela variável LANG, a partir das strings: opac/webapp/translations/messages.pot
# executar: $ LANG=en make create_catalog
create_catalog:
	pybabel init -i opac/webapp/translations/messages.pot -d opac/webapp/translations -l $(LANG)

# atualiza os catalogos, a partir das strings: opac/webapp/translations/messages.pot
update_catalog:
	pybabel update -i opac/webapp/translations/messages.pot -d opac/webapp/translations

# compila as traduções dos .po em arquivos .mo prontos para serem utilizados.
compile_messages:
	pybabel compile -d opac/webapp/translations

build_i18n:
	@make make_messages && make update_catalog && make compile_messages

#########
## test #
#########

test:
	export OPAC_CONFIG="config/templates/testing.template" && python opac/manager.py test

test_coverage:
	export OPAC_CONFIG="config/templates/testing.template" && export FLASK_COVERAGE="1" && python opac/manager.py test

#########
## cache #
#########

invalidate_cache:
	python opac/manager.py invalidate_cache

invalidate_cache_forced:
	python opac/manager.py invalidate_cache	--force_clear


#####################################
## OPAC_STATIC_REPO_PATH - frontend #
#####################################

static_show_repo_dir:
	@echo "using: OPAC_STATIC_REPO_PATH="$(OPAC_STATIC_REPO_PATH)

static_copy_less: static_show_repo_dir
	cp -R $(OPAC_STATIC_REPO_PATH)/static/less ./opac/webapp/static

static_copy_fonts: static_show_repo_dir
	cp -R $(OPAC_STATIC_REPO_PATH)/static/fonts-new ./opac/webapp/static/

static_copy_js_vendor: static_show_repo_dir
	cp -R $(OPAC_STATIC_REPO_PATH)/static/js/vendor ./opac/webapp/static/js/

static_copy_js: static_show_repo_dir
	cp $(OPAC_STATIC_REPO_PATH)/static/js/*.js ./opac/webapp/static/js/

static_copy_all: static_show_repo_dir static_copy_less static_copy_fonts static_copy_js_vendor static_copy_js
	@echo "[COPIADO static/less, static/fonts-new, static/js/vendor e static/js/*.js]"

static_clean_js_bundles:
	@rm -f ./opac/webapp/static/js/scielo-article-standalone.js \
	      ./opac/webapp/static/js/scielo-bundle.js
	@echo 'arquivo JS removidos com sucesso!'

static_clean_all_bundles: static_clean_js_bundles
	@echo 'arquivo JS e CSS removidos com sucesso!'

static_check_deps:
	@echo 'NodeJs version:' $(shell node -v)
	@echo 'npm version:' $(shell npm -v)
	@echo 'Gulp.js version:' $(shell gulp -v)

static_install_deps:
	@echo 'instalando as dependência (package.json):'
	@npm install
