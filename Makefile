
#########
## deps #
#########
update_requirements:
	pip install --upgrade -r requirements.txt

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
