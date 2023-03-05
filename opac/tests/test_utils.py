# coding: utf-8

from unittest.mock import Mock, patch

import webapp
from webapp import utils as wutils

from . import utils
from .base import BaseTestCase


class UtilsTestCase(BaseTestCase):
    # Issue
    def test_get_prev_issue(self):
        """
        Teste da função utils.get_prev_issue().

        IMPORTANTE: A lista é invertida.
        """

        issue1 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "1",
                "order": "1",
            }
        )
        issue2 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "2",
                "order": "2",
            }
        )
        issue3 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "3",
                "order": "3",
            }
        )

        # criando uma lista de números ordenada
        issues = [issue1, issue2, issue3]

        prev_issue = wutils.get_prev_issue(issues, issue2)

        self.assertEqual(prev_issue, issue3)

    def test_get_next_issue(self):
        """
        Teste da função utils.get_next_issue().

        IMPORTANTE: A lista é invertida.
        """

        issue1 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "1",
                "order": "1",
            }
        )
        issue2 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "2",
                "order": "2",
            }
        )
        issue3 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "3",
                "order": "3",
            }
        )

        # criando uma lista de números ordenada
        issues = [issue1, issue2, issue3]

        next_issue = wutils.get_next_issue(issues, issue2)

        self.assertEqual(next_issue, issue1)

    def test_get_prev_issue_with_one_item(self):
        """
        Teste da função utils.get_prev_issue() without itens, deve retorna None.
        """

        issue1 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "1",
                "order": "1",
            }
        )

        issue = utils.makeOneIssue()

        # criando uma lista de números vazia
        issues = [issue1]

        prev_issue = wutils.get_prev_issue(issues, issue)

        self.assertIsNone(prev_issue)

    def test_get_next_issue_with_one_item(self):
        """
        Teste da função utils.get_next_issue() without itens, deve retorna None.
        """

        issue1 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "1",
                "order": "1",
            }
        )

        issue = utils.makeOneIssue()

        # criando uma lista de números vazia
        issues = [issue1]

        next_issue = wutils.get_next_issue(issues, issue)

        self.assertIsNone(next_issue)

    def test_get_prev_issue_when_the_last_issue(self):
        """
        Testando o get_prev_issue quando é acessado um índice inexistente, deve
        retorna None.

        Acessando o a um índice inexistente, o último item da lista irá retornar
        None pois não existe o índice [último] + 1 (Lembrando que a lista de
        número é invertida)

        Portanto a função get_prev_issue soma 1.

        IMPORTANTE: A lista é invertida.
        """

        issue1 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "1",
                "order": "1",
            }
        )
        issue2 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "2",
                "order": "2",
            }
        )
        issue3 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "3",
                "order": "3",
            }
        )
        issue4 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "4",
                "order": "4",
            }
        )

        # criando uma lista de números ordenada
        issues = [issue1, issue2, issue3, issue4]

        prev_issue = wutils.get_prev_issue(issues, issue4)

        self.assertIsNone(prev_issue)

    def test_get_next_issue_when_first_item(self):
        """
        Testando o get_next_issue quando é acessado o primiero índice, deve
        retorna None.

        Acessando o primiero item da lista irá retornar None.

        IMPORTANTE: A lista é invertida.
        """

        issue1 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "1",
                "order": "1",
            }
        )
        issue2 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "2",
                "order": "2",
            }
        )
        issue3 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "3",
                "order": "3",
            }
        )
        issue4 = utils.makeOneIssue(
            {
                "year": "2016",
                "volume": "1",
                "number": "4",
                "order": "4",
            }
        )

        # criando uma lista de números ordenada
        issues = [issue1, issue2, issue3, issue4]

        next_issue = wutils.get_next_issue(issues, issue1)

        self.assertIsNone(next_issue)

    # Article
    def test_get_prev_article(self):
        """
        Teste da função utils.get_prev_article().
        """

        article1 = utils.makeOneArticle(
            {
                "order": "1",
            }
        )
        article2 = utils.makeOneArticle(
            {
                "order": "2",
            }
        )
        article3 = utils.makeOneArticle(
            {
                "order": "3",
            }
        )

        # criando uma lista de artigos ordenada
        articles = [article1, article2, article3]

        prev_article = wutils.get_prev_article(articles, article2)

        self.assertEqual(prev_article, article1)

    def test_get_next_article(self):
        """
        Teste da função utils.get_next_article().
        """

        article1 = utils.makeOneArticle(
            {
                "order": "1",
            }
        )
        article2 = utils.makeOneArticle(
            {
                "order": "2",
            }
        )
        article3 = utils.makeOneArticle(
            {
                "order": "3",
            }
        )

        # criando uma lista de artigos ordenada
        articles = [article1, article2, article3]

        next_article = wutils.get_next_article(articles, article2)

        self.assertEqual(next_article, article3)

    def test_get_next_article_when_last_article(self):
        """
        Teste da função utils.get_next_article(), quando é o último artigo
        deve retorna None.
        """

        article1 = utils.makeOneArticle(
            {
                "order": "1",
            }
        )
        article2 = utils.makeOneArticle(
            {
                "order": "2",
            }
        )
        article3 = utils.makeOneArticle(
            {
                "order": "3",
            }
        )

        # criando uma lista de artigos ordenada
        articles = [article1, article2, article3]

        next_article = wutils.get_next_article(articles, article3)

        self.assertIsNone(next_article)

    def test_get_prev_article_when_first_article(self):
        """
        Teste da função utils.get_prev_article(), quando é o primeiro artigo
        deve retorna None.
        """

        article1 = utils.makeOneArticle(
            {
                "order": "1",
            }
        )
        article2 = utils.makeOneArticle(
            {
                "order": "2",
            }
        )
        article3 = utils.makeOneArticle(
            {
                "order": "3",
            }
        )

        # criando uma lista de artigos ordenada
        articles = [article1, article2, article3]

        prev_article = wutils.get_prev_article(articles, article1)

        self.assertIsNone(prev_article)

    def test_join_html_files_content(self):
        files = ["paboutj.htm", "pedboard.htm", "pinstruc.htm"]
        content = wutils.join_html_files_content(
            "opac/tests/fixtures/pages/revistas", "rbep", files
        )

        self.assertIn(
            "Red de Revistas Científicas de América Latina y "
            "el Caribe, España y Portugal",
            content,
        )
        self.assertIn(
            "Luiz Antunes Netto Carreira, UDESC - "
            "Universidade do Estado de Santa Catarina",
            content,
        )
        self.assertIn(
            "11. O cadastro no sistema e posterior acesso,"
            " por meio de login e senha",
            content,
        )

    @patch.object(wutils.page_migration, "delete_file")
    @patch("requests.get")
    @patch.object(webapp.utils.utils, "create_image")
    @patch.object(webapp.utils.utils, "create_file")
    @patch.object(webapp.utils.utils, "migrate_page_create_image")
    @patch.object(webapp.utils.utils, "migrate_page_create_file")
    @patch.object(webapp.utils.utils, "create_page")
    def test_migrate_page(
        self,
        mocked_create_page,
        mocked_migrate_page_create_file,
        mocked_migrate_page_create_image,
        mocked_create_file,
        mocked_create_image,
        mocked_requests_get,
        mocked_delete_file,
    ):
        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b"content"
        mocked_requests_get.return_value = mocked_response

        mocked_create_file = Mock()
        mocked_create_file.get_absolut_url = "bal"
        mocked_migrate_page_create_image.side_effect = [
            "/media/rbep_abc.jpg",
        ]
        mocked_migrate_page_create_file.side_effect = ["/media/rbep_avaliacao_en.htm"]
        registered_page = Mock()
        registered_page.content = ""
        mocked_create_page.side_effect = registered_page
        mocked_delete_file.side_effect = None
        content = (
            '<img src="/img/revistas/abc.jpg">'
            '<a href="http://www.scielo.br/avaliacao/avaliacao_en.htm"/>'
        )
        new_content = wutils.migrate_page_content(
            content, acron="rbep", page_name=None, language="pt"
        )
        self.assertEqual(
            '<img src="/media/rbep_abc.jpg"/>'
            '<a href="http://www.scielo.br/avaliacao/avaliacao_en.htm"></a>',
            new_content,
        )
