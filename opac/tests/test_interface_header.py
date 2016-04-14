# coding: utf-8

from flask import url_for
from base import BaseTestCase

import utils


class HeaderTestCase(BaseTestCase):

    def test_current_language_when_set_pt_BR(self):
        """
        Teste para alterar o idioma da interface, nesse teste a URL:
        '/set_locale/pt_BR' deve manter na inteface somente o
        idioma Espanhol e Inglês.
        """

        with self.client as c:
            collection = utils.makeOneCollection()
            response = c.get(url_for('main.set_locale', lang_code='pt_BR'),
                             headers={'Referer': '/'},
                             follow_redirects=True)
            self.assertStatus(response, 200)

            self.assertTemplateUsed('collection/index.html')
            self.assertIn('lang-en', response.data)
            self.assertIn('lang-es', response.data)
            self.assertNotIn('lang-pt', response.data)

    def test_current_language_when_set_en(self):
        """
        Teste para alterar o idioma da interface, nesse teste a URL:
        '/set_locale/en' deve manter na inteface somente o
        idioma Espanhol e Português.
        """

        with self.client as c:
            collection = utils.makeOneCollection()
            response = c.get(url_for('main.set_locale', lang_code='en'),
                             headers={'Referer': '/'},
                             follow_redirects=True)
            self.assertStatus(response, 200)

            self.assertTemplateUsed('collection/index.html')
            self.assertIn('lang-pt', response.data)
            self.assertIn('lang-es', response.data)
            self.assertNotIn('lang-en', response.data)

    def test_current_language_when_set_es(self):
        """
        Teste para alterar o idioma da interface, nesse teste a URL:
        '/set_locale/es' deve manter na inteface somente o
        idioma Inglês e Português.
        """

        with self.client as c:
            collection = utils.makeOneCollection()
            response = c.get(url_for('main.set_locale', lang_code='es'),
                             headers={'Referer': '/'},
                             follow_redirects=True)
            self.assertStatus(response, 200)

            self.assertTemplateUsed('collection/index.html')
            self.assertIn('lang-pt', response.data)
            self.assertIn('lang-en', response.data)
            self.assertNotIn('lang-es', response.data)

    def test_current_header_logo_when_set_pt_BR(self):
        """
        Testa se o logo é alterado quando é alterado o idioma na interface,
        nesse teste o logo deve retorna no contexto do idioma Português.
        """

        with self.client as c:
            collection = utils.makeOneCollection()

            response = c.get(url_for('main.set_locale', lang_code='pt_BR'),
                             headers={'Referer': '/'},
                             follow_redirects=True)
            self.assertStatus(response, 200)

            self.assertTemplateUsed('collection/index.html')
            self.assertIn('data-lang="pt_BR"', response.data)

    def test_current_header_logo_when_set_en(self):
        """
        Testa se o logo é alterado quando é alterado o idioma na interface,
        nesse teste o logo deve retorna no contexto do idioma Inglês.
        """

        with self.client as c:
            collection = utils.makeOneCollection()
            response = c.get(url_for('main.set_locale', lang_code='en'),
                             headers={'Referer': '/'},
                             follow_redirects=True)
            self.assertStatus(response, 200)

            self.assertTemplateUsed('collection/index.html')
            self.assertIn('data-lang="en"', response.data)

    def test_current_header_logo_when_set_es(self):
        """
        Testa se o logo é alterado quando é alterado o idioma na interface,
        nesse teste o logo deve retorna no contexto do idioma Espanhol.
        """

        with self.client as c:
            collection = utils.makeOneCollection()
            response = c.get(url_for('main.set_locale', lang_code='es'),
                             headers={'Referer': '/'},
                             follow_redirects=True)
            self.assertStatus(response, 200)

            self.assertTemplateUsed('collection/index.html')
            self.assertIn('data-lang="es"', response.data)


class MenuTestCase(BaseTestCase):

    def test_home_link_is_selected_for_index_view(self):
        """
        Verficamos que o link do menú "Home" tem o css:
        "selected" quando acessamos a view "index"
        """
        response = self.client.get(url_for('main.index'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/index.html')
        expected_anchor = u'<a href="/"\n         class="btn single selected">\n        <span class="glyphBtn home"></span> Home\n      </a>'
        # expected_anchor = u'<a class="btn single " href="/"><span class="glyphBtn home"></span> Home </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_search_link_is_selected_for_search_view(self):
        """
        Verficamos que o link do menú "Buscar artigos" tem o css:
        "selected" quando acessamos a view "search"
        """
        response = self.client.get(url_for('main.search'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/search.html')
        expected_anchor = u'<a href="/search"\n         class="btn single selected">\n        <span class="glyphBtn search"></span>\n        <span class="hidden-sm">Buscar artigos</span>\n        <span class="hidden-md hidden-lg">Buscar</span>\n      </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_alpha_link_is_selected_for_list_alpha(self):
        """
        Verficamos que o link do menú "Alfabética" tem o css:
        "selected" quando acessamos a view "collection_list_alpha"
        """
        response = self.client.get(url_for('main.collection_list_alpha'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_alpha.html')
        expected_anchor = u'<a href="/journals"\n             class="btn group selected">\n            Alfabética\n          </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_theme_link_is_selected_for_list_theme(self):
        """
        Verficamos que o link do menú "Temática" tem o css:
        "selected" quando acessamos a view "collection_list_theme"
        """
        response = self.client.get(url_for('main.collection_list_theme'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_theme.html')
        expected_anchor = u'<a href="/journals/theme"\n             class="btn group selected">\n            Temática\n          </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_institution_link_is_selected_for_list_institution(self):
        """
        Verficamos que o link do menú "Por instituição" tem o css:
        "selected" quando acessamos a view "collection_list_institution"
        """
        response = self.client.get(url_for('main.collection_list_institution'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_institution.html')
        expected_anchor = u'<a href="/journals/institution"\n             class="btn group selected">\n            Por instituição\n          </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_metrics_link_is_selected_for_metric_view(self):
        """
        Verficamos que o link do menú "Métricas" tem o css:
        "selected" quando acessamos a view "metrics"
        """
        response = self.client.get(url_for('main.metrics'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/metrics.html')
        expected_anchor = u'<a href="/metrics"\n         class="btn single selected">\n        <span class="glyphBtn metrics"></span> Métricas\n      </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_about_link_is_selected_for_about_view(self):
        """
        Verficamos que o link do menú "Sobre o Scielo" tem o css:
        "selected" quando acessamos a view "about"
        """
        response = self.client.get(url_for('main.about'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/about.html')
        expected_anchor = u'<a href="/about"\n         class="btn single dropdown-toggle selected">\n        <span class="glyphBtn infoMenu"></span>\n        <span class="hidden-sm">Sobre o SciELO</span>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    # menu hamburger

    def test_links_in_hamburger_menu(self):
        """
        no menú de hamurger, verificamos os links que apontam a views do opac
        """
        response = self.client.get(url_for('main.index'))
        self.assertStatus(response, 200)
        expected_anchor1 = u"""<a href="%s"><strong>SciELO Brasil</strong></a>""" % url_for('.index')
        self.assertIn(expected_anchor1, response.data.decode('utf-8'))
        expected_anchor2 = u"""<li><a href="%s">Lista alfabética de periódicos</a></li>""" % url_for('.collection_list_alpha')
        self.assertIn(expected_anchor2, response.data.decode('utf-8'))
        expected_anchor3 = u"""<li><a href="%s">Lista temática de periódicos</a></li>""" % url_for('.collection_list_theme')
        self.assertIn(expected_anchor3, response.data.decode('utf-8'))
        expected_anchor4 = u"""<li><a href="%s">Busca</a></li>""" % url_for('.search')
        self.assertIn(expected_anchor4, response.data.decode('utf-8'))
        expected_anchor5 = u"""<li><a href="%s">Métricas</a></li>""" % url_for('.metrics')
        self.assertIn(expected_anchor5, response.data.decode('utf-8'))
        expected_anchor6 = u"""<li><a href="%s">Sobre o SciELO Brasil</a></li>""" % url_for('.about')
        self.assertIn(expected_anchor6, response.data.decode('utf-8'))
        expected_anchor7 = u"""<li><a href="#">Contatos</a></li>"""
        self.assertIn(expected_anchor7, response.data.decode('utf-8'))
        expected_anchor8 = u"""<a href="#"><strong>SciELO.org - Rede SciELO</strong></a>"""
        # rede/scielo org
        self.assertIn(expected_anchor8, response.data.decode('utf-8'))
        expected_anchor9 = u"""<li><a href="http://www.scielo.org/php/index.php">Coleções nacionais e temáticas</a></li>"""
        self.assertIn(expected_anchor9, response.data.decode('utf-8'))
        expected_anchor10 = u"""<li><a href="http://www.scielo.org/applications/scielo-org/php/secondLevel.php?xml=secondLevelForAlphabeticList&xsl=secondLevelForAlphabeticList">Lista alfabética de periódicos</a></li>"""
        self.assertIn(expected_anchor10, response.data.decode('utf-8'))
        expected_anchor11 = u"""<li><a href="http://www.scielo.org/applications/scielo-org/php/secondLevel.php?xml=secondLevelForSubjectByLetter&xsl=secondLevelForSubjectByLetter">Lista de periódicos por assunto</a></li>"""
        self.assertIn(expected_anchor11, response.data.decode('utf-8'))
        expected_anchor12 = u"""<li><a href="http://search.scielo.org/">Busca</a></li>"""
        self.assertIn(expected_anchor12, response.data.decode('utf-8'))
        expected_anchor13 = u"""<li><a href="http://www.scielo.org/applications/scielo-org/php/siteUsage.php">Métricas</a></li>"""
        self.assertIn(expected_anchor13, response.data.decode('utf-8'))
        expected_anchor14 = u"""<li><a href="http://www.scielo.org/php/level.php?lang=pt&component=56&item=9">Acesso OAI e RSS</a></li>"""
        self.assertIn(expected_anchor14, response.data.decode('utf-8'))
        expected_anchor15 = u"""<li><a href="http://www.scielo.org/php/level.php?lang=pt&component=56&item=8">Sobre a Rede SciELO</a></li>"""
        self.assertIn(expected_anchor15, response.data.decode('utf-8'))
        expected_anchor16 = u"""<li><a href="#">Contatos</a></li>"""
        self.assertIn(expected_anchor16, response.data.decode('utf-8'))
        expected_anchor17 = u"""<a href="#"><strong>Portal do Autor</strong></a>"""
        self.assertIn(expected_anchor17, response.data.decode('utf-8'))

    def test_blog_link_in_hamburger_menu(self):
        """
        Verificamos que o link para o blog em perspectiva fique
        apontando ao link certo considerando o idioma da sessão
        """
        with self.client as c:
            collection = utils.makeOneCollection()
            # idioma em 'pt_br'
            response = c.get(
                url_for('main.set_locale', lang_code='pt_BR'),
                headers={'Referer': '/'},
                follow_redirects=True)

            self.assertStatus(response, 200)
            expected_anchor = '<a href="http://blog.scielo.org/">'
            self.assertIn(expected_anchor, response.data.decode('utf-8'))

            # idioma em 'en'
            response = c.get(
                url_for('main.set_locale', lang_code='en'),
                headers={'Referer': '/'},
                follow_redirects=True)

            self.assertStatus(response, 200)
            expected_anchor = '<a href="http://blog.scielo.org/en/">'
            self.assertIn(expected_anchor, response.data.decode('utf-8'))

            # idioma em 'es'
            response = c.get(
                url_for('main.set_locale', lang_code='es'),
                headers={'Referer': '/'},
                follow_redirects=True)

            self.assertStatus(response, 200)
            expected_anchor = '<a href="http://blog.scielo.org/es/">'
            self.assertIn(expected_anchor, response.data.decode('utf-8'))
