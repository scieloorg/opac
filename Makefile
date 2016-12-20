default: test

COMPOSE_FILE_DEV = docker-compose-dev.yml
OPAC_BUILD_DATE= $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
OPAC_VCS_REF= $(shell git rev-parse --short HEAD)
OPAC_WEBAPP_VERSION=$(strip $(shell cat VERSION))

############################################
## atalhos docker-compose desenvolvimento ##
############################################

dev_compose_build:
	docker-compose -f $(COMPOSE_FILE_DEV) build

dev_compose_up:
	docker-compose -f $(COMPOSE_FILE_DEV) up -d

dev_compose_logs:
	docker-compose -f $(COMPOSE_FILE_DEV) logs -f

dev_compose_stop:
	docker-compose -f $(COMPOSE_FILE_DEV) stop

dev_compose_ps:
	docker-compose -f $(COMPOSE_FILE_DEV) ps

dev_compose_rm:
	docker-compose -f $(COMPOSE_FILE_DEV) rm -f

dev_compose_exec_shell_webapp:
	docker-compose -f $(COMPOSE_FILE_DEV) exec opac_webapp sh

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
