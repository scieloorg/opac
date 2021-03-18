# coding: utf-8
# import unittest
# from unittest.mock import patch, Mock
from unittest.mock import patch

import flask
from flask import url_for, g, current_app
# from flask import render_template
# from flask_babelex import gettext as _

from .base import BaseTestCase

from . import utils


class TestArticleDetailV3Abstract(BaseTestCase):
    def _get_response(self, article_data=None, part='abstract', pid_v2=None,
                      abstract_lang=None):
        with current_app.test_request_context():
            utils.makeOneCollection()
            self.journal = utils.makeOneJournal()
            issue = utils.makeOneIssue({'journal': self.journal})

            _article_data = {
                'title': 'Article Y',
                'original_language': 'en',
                'languages': ['es', 'pt', 'en'],
                'issue': issue,
                'journal': self.journal,
                'abstracts': [
                    {"language": "en", "text": "Abstract in English"},
                ],
                'url_segment': '10-11',
                'translated_titles': [
                    {'language': 'es', 'name': u'Artículo en español'},
                    {'language': 'pt', 'name': u'Artigo en Português'},
                ],
                'pid': 'pidv2'
            }
            _article_data.update(article_data or {})
            self.article = utils.makeOneArticle(_article_data)
            if pid_v2:
                url = '%s?script=sci_abstract&pid=%s' % (
                        url_for('main.router_legacy'), pid_v2)
            else:
                url = url_for(
                    'main.article_detail_v3',
                    url_seg=self.journal.url_segment,
                    article_pid_v3=self.article.aid,
                    part=part,
                    lang=abstract_lang,
                )
            response = self.client.get(url)
            return response

    def test_abstract_pid_v3_returns_404_and_displays_invalid_part_value_message(self):
        expected = "Não existe 'abst'. No seu lugar use 'abstract'"
        response = self._get_response(part='abst')
        self.assertStatus(response, 404)
        result = response.data.decode('utf-8')
        self.assertIn(expected, result)

    def test_abstract_pid_v3_returns_status_code_200(self):
        response = self._get_response(abstract_lang="en")
        self.assertStatus(response, 200)

    @patch("webapp.main.views.render_html")
    def test_abstract_pid_v3(self, mock_render_html):
        mock_render_html.return_value = (
            "abstract do documento",
            ['en', 'es', 'pt'],
        )
        expected = "abstract do documento"
        response = self._get_response(abstract_lang="en")
        result = response.data.decode('utf-8')
        mock_render_html.assert_called_once_with(self.article, "en", True)
        self.assertIn(expected, result)

    @patch("webapp.main.views.render_html")
    def test_abstract_pid_v3_does_not_return_abstract_but_fulltext_if_part_is_None(self, mock_render_html):
        mock_render_html.return_value = (
            "texto do documento",
            ['en', 'es', 'pt'],
        )
        expected = "texto do documento"
        response = self._get_response(part=None)
        result = response.data.decode('utf-8')
        mock_render_html.assert_called_once_with(self.article, "en", False)
        self.assertIn(expected, result)

    def test_abstract_pid_v3_returns_404_because_lang_is_missing(self):
        expected = "Não existe 'False'. No seu lugar use 'abstract'"
        response = self._get_response(part=False)
        self.assertStatus(response, 404)
        result = response.data.decode('utf-8')
        self.assertIn(expected, result)

    def test_abstract_pid_v3_returns_404_and_displays_invalid_part_value_message_if_part_is_False(self):
        expected = "Não existe 'False'. No seu lugar use 'abstract'"
        response = self._get_response(part=False)
        self.assertStatus(response, 404)
        result = response.data.decode('utf-8')
        self.assertIn(expected, result)

    @patch("webapp.main.views.render_html")
    def test_router_legacy_calls(self, mock_f):
        response = self._get_response(pid_v2='pidv2')
        self.assertRedirects(
            response,
            url_for(
                'main.article_detail_v3',
                url_seg=self.journal.url_segment,
                article_pid_v3=self.article.aid,
                part='abstract',
                lang="en",
            ),
        )
