# coding: utf-8

from .base import BaseTestCase

from webapp.utils import related_articles_urls as related_links


class UtilsGScholarTestCase(BaseTestCase):

    def test_get_scholar_urls(self):
        content = '<a href="/scholar?q=a"/><a href="/scholar?q=related:"/><a href="/scholar?q=b"/>'
        result = related_links.get_scholar_urls(content)
        expected = ['/scholar?q=a', '/scholar?q=related:', '/scholar?q=b']
        self.assertEqual(expected, result)

    def test_get_results_searched_by_article_titles(self):
        expected = [
            related_links.URL_GSCHOLAR + 'title1',
            related_links.URL_GSCHOLAR + 'title2',
        ]
        result = related_links.get_scholar_results_searched_by_article_titles(
            ['title1', 'title2'])
        self.assertEqual(expected, result)

    def test_get_results_searched_by_article_url(self):
        article_page_url = 'http://www.scielo.br/scielo.php?pid=S0100-879X2004000400003&script=sci_arttext'
        expected = related_links.URL_GSCHOLAR + article_page_url
        result = related_links.get_scholar_results_searched_by_article_url(
            article_page_url)
        self.assertEqual(expected, result)

    def test_get_cited_and_related_article_urls(self):
        article_page_url = 'http://www.scielo.br/scielo.php?pid=S0100-879X2004000400003&script=sci_arttext'
        titles = [
            'Genome features of Leptospira interrogans serovar Copenhageni',
        ]
        result = related_links.get_scholar_cited_and_related_article_urls(
            article_page_url, titles)
        self.assertEqual(len(result), 2)
        self.assertIn('cites=', result[0])
        self.assertIn('q=related:', result[1])

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
