======================================
SciELO - On-line Public Access Catalog
======================================

.. image:: https://travis-ci.org/scieloorg/opac.svg?branch=master
        :target: https://travis-ci.org/scieloorg/opac

.. image:: https://landscape.io/github/scieloorg/opac/master/landscape.svg?style=flat
        :target: https://landscape.io/github/scieloorg/opac/master
        :alt: Code Health

.. image:: https://pyup.io/repos/github/scieloorg/opac/shield.svg
        :target: https://pyup.io/repos/github/scieloorg/opac/
        :alt: Updates

.. image:: https://pyup.io/repos/github/scieloorg/opac/python-3-shield.svg
        :target: https://pyup.io/repos/github/scieloorg/opac/
        :alt: Python 3

.. image:: https://images.microbadger.com/badges/image/scieloorg/opac.svg
        :target: https://microbadger.com/images/scieloorg/opac
        :alt: Image info from microbadger.com

.. image:: https://images.microbadger.com/badges/version/scieloorg/opac.svg
        :target: https://microbadger.com/images/scieloorg/opac
        :alt: Image latest version

.. image:: https://images.microbadger.com/badges/commit/scieloorg/opac.svg
        :target: https://microbadger.com/images/scieloorg/opac
        :alt: Image latest commit


=========================
Instalação e configuração
=========================

Em nossa `wiki <https://github.com/scieloorg/opac/wiki>`_ você tem as diferentes guias de instalação e configuração para diferentes ambientes:

- `De desenvolvimento <https://github.com/scieloorg/opac/wiki/Configura%C3%A7%C3%A3o-e-instala%C3%A7%C3%A3o>`_
- `De produção com Gunicorn/Nginx/Supervisor em CentOS <https://github.com/scieloorg/opac/wiki/Configura%C3%A7%C3%A3o-e-instala%C3%A7%C3%A3o-%28ambiente-de-produ%C3%A7%C3%A3o%29-Gunicorn>`_
- `De produção com Chaussette/Nginx/Circus em CentOS <https://github.com/scieloorg/opac/wiki/Configura%C3%A7%C3%A3o-e-instala%C3%A7%C3%A3o-%28ambiente-de-produ%C3%A7%C3%A3o%29-Gunicorn>`_


============================
Guia de configuração do site
============================

Pode acessar `nossa wiki <https://github.com/scieloorg/opac/wiki/Configura%C3%A7%C3%A3o-padr%C3%A3o-e-vari%C3%A1veis-de-ambiente>`_ para ter uma guia completa e como ajustar a configuração a partir de un arquivo de configuração em cada instância ou utilizando variáveis de ambiente.


======================
Como executar os tests
======================


- Para rodar os tests de unidade, pode executar: ``make test``
- Para ter o relatório de coverage deve executar: ``make test_coverage``


===========================================
Arquivos: Dockerfile* e docker-compose*.yml
===========================================


- **Dockerfile**: contém as definições para construir a imagem pronta para instalar em **produção**
- **Dockerfile-dev**: contém as definições para construir a imagem pronta para instalar em **desenvolvimento**

- **docker-compose.yml**: contém as definições para iniciar todos os containers necessários para rodar em **produção**
- **docker-compose-build.yml**: contém as definições para construir as imagems e iniciar todos os containers necessários para rodar no **Travis/CI**
- **docker-compose-dev.yml**: contém as definições para iniciar todos os containers necessários para rodar em **desenvolvimento**


=================================================
Instalação utilizando Docker para desenvolvimento
=================================================


Para executar o ambiente (de desenvolvimento) com Docker, utilizando as definições do arquivo **Dockerfile-dev** e **docker-compose.yml-dev** na raiz do projeto.
Simplesmente executar:

1. executar: ``make dev_compose_build`` para construir a imagem do OPAC.
2. executar: ``make dev_compose_up``  para rodar os containers.
3. acessar pelo browser: http://localhost ou no caso de utilizar OSx trocar localhost pela IP da maquina default (ver na saída do comando: ``docker-machine ip``)
4. para inspecionar os logs, executar: ``make dev_compose_logs``
5. para parar os containers, executar: ``make dev_compose_stop``
6. para abrir uma terminal dentro do container, executar: ``make dev_compose_exec_shell_webapp``

======================
Fixtures
======================

Procedimento para popular a instância de desenvolvimento, a partir de fixtures disponibilizadas pelo SciELO.

1. Baixar a fixture de desenvolvimento, execute: ``wget https://minio.scielo.br/dev/fixtures/opac_br.zip``
2. Extraia o conteúdo, execute: ``unzip opac_br.zip`
3. Repare que contém uma pasta chamado **opac_br**, nessa pasta temos os arquivo **.bson .json .sqlite** e outra pasta chamado **media** contento os ativos dos periódico e da coleção.
4. Acesse a pasta **opac_br**, execute: ``cd opac_br``
5. Utilizando **mongorestore** realize o recuperação do banco de dados apontando para o endereço que está rodando o seu mongo local, exemplo: ``mongorestore --host=localhost --port=27017 --db=opac_br -d``
6. Realize a cópia da pasta **media** para {APP}/data
7. Realize a cópia do **opac.sqlite** para {APP}/data
8. Para ambiente utilizando **Docker** é necessário reiniciar os containers: ``make dev_compose_stop`` && ``make dev_compose_up``

Caso não tenha o **mongorestore** localmente é necessário a instalação **MONGODB DATABASE TOOLS**: https://docs.mongodb.com/database-tools/installation/installation/

Para utilizar o ambiente de desenvolvimento com os dados populado a partir dos passos indicado acima é necessário que esteja conectado com a **VPN da SciELO**

Usuário e senha para a área administrativa:

**Ususário:** admin@admin.com
**Senha:** admin


=========================================
Reportar problemas, ou solicitar mudanças
=========================================


Para reportar problemas, bugs, ou simplesmente solicitar alguma nova funcionalidade, pode `criar um ticket <https://github.com/scieloorg/opac/issues>`_ com seus pedidos.


=========================================
Equipe responsável por instalação, desenvolvimento e manutenção
=========================================

- Jamil Atta Junior (Desenvolvimento) <jamil.atta@scielo.org>
- Juan Funez (Desenvolvimento) <juan.funez@scielo.org>
- Rondineli Gama Saad (Infraestrutura) <rondineli.saad@scielo.org>
