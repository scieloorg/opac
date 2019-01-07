# coding: utf-8

from .base import BaseTestCase

from webapp.utils import related_articles_urls as related_links


class UtilsGScholarTestCase(BaseTestCase):

    def test_get_google_results_searched_by_article_titles(self):
        expected = [
            'https://www.google.com/search?q=title 1',
            'https://www.google.com/search?q=title 2!',
        ]
        result = related_links.get_google_results_searched_by_article_titles(
            ['title 1', 'title 2!'])
        self.assertEqual(expected, result)

    def test_get_scholar_results_searched_by_article_titles(self):
        expected = [
            'https://scholar.google.com/scholar?q=title 1',
            'https://scholar.google.com/scholar?q=title 2!',
        ]
        result = related_links.get_scholar_results_searched_by_article_titles(
            ['title 1', 'title 2!'])
        self.assertEqual(expected, result)

    def test_related_links(self):
        article_page_url = 'http://www.scielo.br/scielo.php?pid=S0100-879X2004000400003&script=sci_arttext'
        titles = [
            'Genome features of Leptospira interrogans serovar Copenhageni',
        ]
        result = related_links.related_links(article_page_url, titles)
        self.assertEqual(result[0][0], "Google")
        self.assertEqual(result[0][1], "Similares no")
        self.assertEqual(result[0][2], "https://www.google.com/search?q=Genome features of Leptospira interrogans serovar Copenhageni")
        self.assertEqual(result[1][0], "Google Scholar")
        self.assertEqual(result[1][1], "Citados e Similares no")
        self.assertEqual(result[1][2], 'https://scholar.google.com/scholar?q=Genome features of Leptospira interrogans serovar Copenhageni')
