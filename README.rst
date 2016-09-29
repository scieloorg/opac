======================================
SciELO - On-line Public Access Catalog
======================================

.. image:: https://travis-ci.org/scieloorg/opac.svg
    :target: https://travis-ci.org/scieloorg/opac


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


=================================================
Instalação utilizando Docker para desenvolvimento
=================================================

Para executar o ambiente (de desenvolvimento) com Docker, utilizando as definições do arquivo **Dockerfile** e **docker-compose.yml** na raiz do projeto.
Simplesmente executar:

1. executar: ``docker-compose -f docker-compose-dev.yml build`` para construir as imagens.
2. executar: ``docker-compose -f docker-compose-dev.yml up``  para rodar os containers.
3. acessar pelo browser: http://localhost ou no caso de utilizar OSx trocar localhost pela IP da maquina default (ver na saída do comando: ``docker-machine ip``)
4. para parar os containers, executar: ``docker-compose -f docker-compose-dev.yml stop``
5. para remover os containers, executar: ``docker-compose -f docker-compose-dev.yml rm`` e confirmar com ``y``

=========================================
Reportar problemas, ou solicitar mudanças
=========================================

Para reportar problemas, bugs, ou simplesmente solicitar alguma nova funcionalidade, pode `criar um ticket <https://github.com/scieloorg/opac/issues>`_ com seus pedidos.

