
#########
## i18n #
#########

# Faz um scan em toda a app buscando strings traduzíveis e o resultado fica em app/translations/messages.pot
make_messages:
	pybabel extract -F config/babel.cfg -k lazy_gettext -o app/translations/messages.pot .

# cria o catalogo para o idioma definido pela variável LANG, a partir das strings: app/translations/messages.pot
# executar: $ LANG=en make create_catalog
create_catalog:
	pybabel init -i app/translations/messages.pot -d app/translations -l $(LANG)

# atualiza os catalogos, a partir das strings: app/translations/messages.pot
update_catalog:
	pybabel update -i app/translations/messages.pot -d app/translations

# compila as traduções dos .po em arquivos .mo prontos para serm utilizados.
compile_messages:
	pybabel compile -d app/translations

#########
## test #
#########

test:
	export OPAC_CONFIG="config.testing" && python manager.py test
