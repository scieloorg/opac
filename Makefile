default: test

COMPOSE_FILE_DEV = docker-compose-dev.yml
COMPOSE_FILE_BUILD = docker-compose-build.yml

OPAC_BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
OPAC_VCS_REF=$(strip $(shell git rev-parse --short HEAD))
OPAC_WEBAPP_VERSION=$(strip $(shell cat VERSION))

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
	@docker-compose -f $(COMPOSE_FILE_DEV) logs -f

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

#########
## test #
#########

test:
	export OPAC_CONFIG="config/templates/testing.template" && python opac/manager.py test

test_coverage:
	export OPAC_CONFIG="config/templates/testing.template" && export FLASK_COVERAGE="1" && python opac/manager.py test
