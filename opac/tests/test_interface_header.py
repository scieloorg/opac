# coding: utf-8

from flask import url_for
from base import BaseTestCase


class HeaderTestCase(BaseTestCase):

    def test_current_language_when_set_pt_BR(self):
        """
        Teste para alterar o idioma da interface, nesse teste a URL:
        '/set_locale/pt_BR' deve manter na inteface somente o
        idioma Espanhol e Inglês.
        """

        with self.client as c:
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
            response = c.get(url_for('main.set_locale', lang_code='es'),
                             headers={'Referer': '/'},
                             follow_redirects=True)
            self.assertStatus(response, 200)

            self.assertTemplateUsed('collection/index.html')
            self.assertIn('lang-pt', response.data)
            self.assertIn('lang-en', response.data)
            self.assertNotIn('lang-es', response.data)
