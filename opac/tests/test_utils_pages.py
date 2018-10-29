# coding: utf-8

import os
from .base import BaseTestCase

from webapp.utils.page import (
    Page,
)


REVISTAS_PATH = 'opac/tests/fixtures/pages/revistas'
IMG_REVISTAS_PATH = 'opac/tests/fixtures/pages/img_revistas'


class UtilsPageTestCase(BaseTestCase):

    def setUp(self):
        content = ''
        original_website = 'http://www.scielo.br'
        revistas_path = REVISTAS_PATH
        img_revistas_path = IMG_REVISTAS_PATH
        page_path = '/pages'
        page_name = None
        lang = None
        self.page = Page(content, original_website, revistas_path,
                         img_revistas_path, page_path, page_name, lang)

    def test_content(self):
        self.page.content = '<html><body>x</body></html>'
        self.assertEqual(self.page.content, '<html><body>x</body></html>')

    def test_original_web_site(self):
        self.assertEqual(self.page.original_website, 'www.scielo.br')

    def test_find_original_website_reference(self):
        self.page.content = '''<img src="www.scielo.br"/>
                            <img src="www.scielo.br/abc"/>
                            <img src="/img/revistas/abc.jpg"/>
                            <img src="www.scielo.br/abc/iaboutj.htm"/>
                            <img src="scielo.br/img/revistas"/>'''

        result = self.page.find_original_website_reference('img', 'src')
        self.assertEqual(result[0]['src'], 'www.scielo.br')
        self.assertEqual(result[1]['src'], 'www.scielo.br/abc')
        self.assertEqual(result[2]['src'], 'www.scielo.br/abc/iaboutj.htm')
        self.assertEqual(len(result), 3)

    def test_new_author(self):
        old = 'http://www.scielo.br/cgi-bin/wxis.exe/iah/' + \
              '?IsisScript=iah/iah.xis&' + \
              'base=article%5Edlibrary&format=iso.pft&lang=p&' + \
              'nextAction=lnk&' + \
              'indexSearch=AU&exprSearch=MEIERHOFFER,+LILIAN+KOZSLOWSKI'
        new = '//search.scielo.org/?q=au:MEIERHOFFER,+LILIAN+KOZSLOWSKI'
        self.assertEqual(new, self.page.new_author_page(old))

    def test_replace_by_relative_url_pdf(self):
        old = 'www.scielo.br/revistas/icse/levels.pdf'
        new = '/revistas/icse/levels.pdf'
        self.assertEqual(new, self.page.replace_by_relative_url(old))

    def test_replace_by_relative_url_pdf_img_revistas(self):
        old = 'www.scielo.br/img/revistas/icse/levels.pdf'
        new = '/img/revistas/icse/levels.pdf'
        self.assertEqual(new, self.page.replace_by_relative_url(old))

    def test_replace_by_relative_url(self):
        old = 'http://www.scielo.br'
        new = '/'
        self.assertEqual(new, self.page.replace_by_relative_url(old))

    def test_replace_by_relative_url_scielo_php(self):
        old = 'http://www.scielo.br/scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso'
        new = '/scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso'
        self.assertEqual(new, self.page.replace_by_relative_url(old))

    def test_link_display_text_1(self):
        expected = 'www.scielo.br/revistas/icse/levels.pdf'
        text = self.page.link_display_text(
            '/revistas/icse/levels.pdf',
            'www.scielo.br/revistas/icse/levels.pdf',
            'www.scielo.br/revistas/icse/levels.pdf')
        self.assertEqual(text, expected)

    def test_link_display_text_2(self):
        expected = 'www.scielo.br/img/revistas/icse/levels.pdf'
        text = self.page.link_display_text(
            '/img/revistas/icse/levels.pdf',
            'www.scielo.br/img/revistas/icse/levels.pdf',
            'www.scielo.br/img/revistas/icse/levels.pdf')
        self.assertEqual(text, expected)

    def test_link_display_text_3(self):
        expected = 'www.scielo.br/journal/icse/about/#instructions'
        text = self.page.link_display_text(
            '/journal/icse/about/#instructions',
            'www.scielo.br/revistas/icse/iinstruc.htm',
            'www.scielo.br/revistas/icse/iinstruc.htm')
        self.assertEqual(text, expected)

    def test_link_display_text_4(self):
        expected = 'www.scielo.br'
        text = self.page.link_display_text(
            '/',
            'www.scielo.br',
            'www.scielo.br ')
        self.assertEqual(text, expected)

    def test_guess_file_location_img_revistas(self):
        expected = os.path.join(
            'opac/tests/fixtures/pages/img_revistas', 'abc.jpg')
        text = self.page.guess_file_location(
            'www.scielo.br/img/revistas/abc.jpg'
        )
        self.assertEqual(text, expected)

    def test_guess_file_location_revistas(self):
        expected = os.path.join(
            'opac/tests/fixtures/pages/revistas', 'abc.jpg')
        text = self.page.guess_file_location(
            'wwww.scielo.br/revistas/abc.jpg'
        )
        self.assertEqual(text, expected)

    def test_guess_file_location_page(self):
        expected = '/pages/abc/abc.jpg'
        text = self.page.guess_file_location('www.scielo.br/abc/abc.jpg')
        self.assertEqual(text, expected)

    def test_guess_file_location_page_relative(self):
        expected = '/pages/abc/abc.jpg'
        text = self.page.guess_file_location('/abc/abc.jpg')
        self.assertEqual(text, expected)

    def test_get_new_file_name(self):
        expected = 'criterio-brasil.jpg'
        ret = self.page.get_slug_name('/abc/abc/Critério_Brasil.jpg')
        self.assertEqual(ret, expected)
