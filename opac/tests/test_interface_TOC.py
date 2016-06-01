# coding: utf-8

import flask
from flask import url_for, current_app

from base import BaseTestCase

import utils


class TOCTestCase(BaseTestCase):

    # TOC
    def test_the_title_of_the_article_list_when_language_PT(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma Português.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = [{'name': "Artigo Com Título Em Português", 'language': 'pt'},
                                 {'name': "Título Del Artículo En Portugués", 'language': 'es'},
                                 {'name': "Article Title In Portuguese", 'language': 'en'}]

            article = utils.makeOneArticle({'issue': issue,
                                            'title': 'Article Y',
                                            'translated_titles': translated_titles})

            header = {'Referer': url_for('main.issue_toc',
                                         issue_id=issue.iid)}

            response = c.get(url_for('main.set_locale',
                                     lang_code='pt_BR'),
                             headers=header,
                             follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'pt_BR')

            self.assertIn(u"Artigo Com Título Em Português",
                          response.data.decode('utf-8'))

    def ttest_the_title_of_the_article_list_when_language_ES(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma Espanhol.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = [{'name': "Artigo Com Título Em Português", 'language': 'pt'},
                                 {'name': "Título Del Artículo En Portugués", 'language': 'es'},
                                 {'name': "Article Title In Portuguese", 'language': 'en'}]

            article = utils.makeOneArticle({'issue': issue,
                                            'title': 'Article Y',
                                            'translated_titles': translated_titles})

            header = {'Referer': url_for('main.issue_toc',
                                         issue_id=issue.iid)}

            response = c.get(url_for('main.set_locale',
                                     lang_code='es'),
                             headers=header,
                             follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'es')

            self.assertIn(u"Título Del Artículo En Portugués",
                          response.data.decode('utf-8'))

    def test_the_title_of_the_article_list_when_language_EN(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma Inglês.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = [{'name': "Artigo Com Título Em Português", 'language': 'pt'},
                                 {'name': "Título Del Artículo En Portugués", 'language': 'es'},
                                 {'name': "Article Title In Portuguese", 'language': 'en'}]

            article = utils.makeOneArticle({'issue': issue,
                                            'title': 'Article Y',
                                            'translated_titles': translated_titles})

            header = {'Referer': url_for('main.issue_toc',
                                         issue_id=issue.iid)}

            response = c.get(url_for('main.set_locale',
                                     lang_code='en'),
                             headers=header,
                             follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'en')

            self.assertIn(u"Article Title In Portuguese",
                          response.data.decode('utf-8'))

    def test_the_title_of_the_article_list_without_translated(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma original quando não tem idioma.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = []

            article = utils.makeOneArticle({'issue': issue,
                                            'title': 'Article Y',
                                            'translated_titles': translated_titles})

            header = {'Referer': url_for('main.issue_toc',
                                         issue_id=issue.iid)}

            response = c.get(url_for('main.set_locale',
                                     lang_code='en'),
                             headers=header,
                             follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'en')

            self.assertIn(u"Article Y",
                          response.data.decode('utf-8'))

    def test_the_title_of_the_article_list_without_unknow_language_for_article(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma original quando não conhece o idioma.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = []

            article = utils.makeOneArticle({'issue': issue,
                                            'title': 'Article Y',
                                            'translated_titles': translated_titles})

            header = {'Referer': url_for('main.issue_toc',
                                         issue_id=issue.iid)}

            response = c.get(url_for('main.set_locale',
                                     lang_code='es_MX'),
                             headers=header,
                             follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'es_MX')

            self.assertIn(u"Article Y",
                          response.data.decode('utf-8'))

    def test_the_title_of_the_article_list_with_and_without_translated(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma original para artigos que não tem tradução e o título traduzido
        quando tem tradução do título.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = [{'name': "Artigo Com Título Em Português", 'language': 'pt'},
                                 {'name': "Título Del Artículo En Portugués", 'language': 'es'},
                                 {'name': "Article Title In Portuguese", 'language': 'en'}]

            article1 = utils.makeOneArticle({'issue': issue,
                                             'title': 'Article Y',
                                             'translated_titles': translated_titles})

            article2 = utils.makeOneArticle({'issue': issue,
                                             'title': 'Article Y',
                                             'translated_titles': []})

            header = {'Referer': url_for('main.issue_toc',
                                         issue_id=issue.iid)}

            response = c.get(url_for('main.set_locale',
                                     lang_code='es'),
                             headers=header,
                             follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'es')

            self.assertIn(u"Article Y",
                          response.data.decode('utf-8'))

            self.assertIn(u"Título Del Artículo En Portugués",
                          response.data.decode('utf-8'))
