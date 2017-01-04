# coding: utf-8

import flask
from flask import url_for

from .base import BaseTestCase

from . import utils


class TOCTestCase(BaseTestCase):

    # TOC
    def test_the_title_of_the_article_list_when_language_pt(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma Português.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = [
                {'name': "Artigo Com Título Em Português", 'language': 'pt'},
                {'name': "Título Del Artículo En Portugués", 'language': 'es'},
                {'name': "Article Title In Portuguese", 'language': 'en'}
            ]

            utils.makeOneArticle({
                'issue': issue,
                'title': 'Article Y',
                'translated_titles': translated_titles
            })

            header = {
                'Referer': url_for(
                    'main.issue_toc',
                    url_seg=journal.url_segment,
                    url_seg_issue=issue.url_segment)
            }

            set_locale_url = url_for('main.set_locale', lang_code='pt_BR')
            response = c.get(set_locale_url, headers=header, follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'pt_BR')

            self.assertIn("Artigo Com Título Em Português", response.data.decode('utf-8'))

    def ttest_the_title_of_the_article_list_when_language_es(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma Espanhol.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = [
                {'name': "Artigo Com Título Em Português", 'language': 'pt'},
                {'name': "Título Del Artículo En Portugués", 'language': 'es'},
                {'name': "Article Title In Portuguese", 'language': 'en'}
            ]

            utils.makeOneArticle({
                'issue': issue,
                'title': 'Article Y',
                'translated_titles': translated_titles
            })

            header = {
                'Referer': url_for(
                    'main.issue_toc',
                    url_seg=journal.url_segment,
                    url_seg_issue=issue.url_segment)}

            set_locale_url = url_for('main.set_locale', lang_code='es')
            response = c.get(set_locale_url, headers=header, follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'es')

            self.assertIn("Título Del Artículo En Portugués",
                          response.data.decode('utf-8'))

    def test_the_title_of_the_article_list_when_language_en(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma Inglês.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = [
                {'name': "Artigo Com Título Em Português", 'language': 'pt'},
                {'name': "Título Del Artículo En Portugués", 'language': 'es'},
                {'name': "Article Title In Portuguese", 'language': 'en'}
            ]

            utils.makeOneArticle({
                'issue': issue,
                'title': 'Article Y',
                'translated_titles': translated_titles
            })

            header = {
                'Referer': url_for(
                    'main.issue_toc',
                    url_seg=journal.url_segment,
                    url_seg_issue=issue.url_segment)
            }

            set_locale_url = url_for('main.set_locale', lang_code='en')
            response = c.get(set_locale_url, headers=header, follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'en')

            self.assertIn("Article Title In Portuguese", response.data.decode('utf-8'))

    def test_the_title_of_the_article_list_without_translated(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma original quando não tem idioma.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = []

            utils.makeOneArticle({
                'issue': issue,
                'title': 'Article Y',
                'translated_titles': translated_titles
            })

            header = {
                'Referer': url_for(
                    'main.issue_toc',
                    url_seg=journal.url_segment,
                    url_seg_issue=issue.url_segment)
            }

            set_locale_url = url_for('main.set_locale', lang_code='en')
            response = c.get(set_locale_url, headers=header, follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'en')

            self.assertIn("Article Y", response.data.decode('utf-8'))

    def test_the_title_of_the_article_list_without_unknow_language_for_article(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma original quando não conhece o idioma.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = []

            utils.makeOneArticle({
                'issue': issue,
                'title': 'Article Y',
                'translated_titles': translated_titles
            })

            header = {
                'Referer': url_for(
                    'main.issue_toc',
                    url_seg=journal.url_segment,
                    url_seg_issue=issue.url_segment)
            }

            set_locale_url = url_for('main.set_locale', lang_code='es_MX')
            response = c.get(set_locale_url, headers=header, follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'es_MX')

            self.assertIn("Article Y", response.data.decode('utf-8'))

    def test_the_title_of_the_article_list_with_and_without_translated(self):
        """
        Teste para verificar se a interface do TOC esta retornando o título no
        idioma original para artigos que não tem tradução e o título traduzido
        quando tem tradução do título.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal})

            translated_titles = [
                {'name': "Artigo Com Título Em Português", 'language': 'pt'},
                {'name': "Título Del Artículo En Portugués", 'language': 'es'},
                {'name': "Article Title In Portuguese", 'language': 'en'}
            ]

            utils.makeOneArticle({
                'issue': issue,
                'title': 'Article Y',
                'translated_titles': translated_titles
            })

            utils.makeOneArticle({
                'issue': issue,
                'title': 'Article Y',
                'translated_titles': []
            })

            header = {
                'Referer': url_for(
                    'main.issue_toc',
                    url_seg=journal.url_segment,
                    url_seg_issue=issue.url_segment)
            }

            set_locale_url = url_for('main.set_locale', lang_code='es')
            response = c.get(set_locale_url, headers=header, follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'es')

            self.assertIn("Article Y", response.data.decode('utf-8'))

            self.assertIn("Título Del Artículo En Portugués", response.data.decode('utf-8'))
