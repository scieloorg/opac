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
