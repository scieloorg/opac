# coding: utf-8

import os
from .base import BaseTestCase

from unittest.mock import patch
from webapp.utils.page import (
    Page, JournalPage, new_author_url_page
)


REVISTAS_PATH = 'htdocs/revistas'
IMG_REVISTAS_PATH = 'htdocs/img/revistas'
HTDOCS = 'htdocs'


class UtilsPageTestCase(BaseTestCase):

    def setUp(self):
        content = ''
        original_website = 'http://www.scielo.br'
        revistas_path = REVISTAS_PATH
        img_revistas_path = IMG_REVISTAS_PATH
        static_files_path = HTDOCS
        page_name = 'criterios'
        lang = 'es'
        self.page = Page(content, original_website, revistas_path,
                         img_revistas_path, static_files_path, page_name, lang)

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
        self.assertEqual(new, new_author_url_page(old))

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

    def test_replace_by_relative_url_any_image(self):
        old = 'http://www.scielo.br/abc/img2.jpg'
        new = '/abc/img2.jpg'
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

    def test_migrate_urls(self):
        self.page.content = '''
            <img src="/img/revistas/img1.jpg"/>
            <img src="http://www.scielo.br/abc/img2.jpg"/>
            <img src="/revistas/img3.jpg"/>
            <img src="http://www.scielo.org/local/Image/scielo20_pt.png"/>'''

        self.page.migrate_urls()

        results = [img['src'] for img in self.page.images]
        expected_items = [
             '/img/revistas/img1.jpg',
             '/abc/img2.jpg',
             '/revistas/img3.jpg',
             'http://www.scielo.org/local/Image/scielo20_pt.png'
            ]
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
        self.assertEqual(results, expected_items)

    def test_migrate_urls_files(self):
        self.page.content = '''
            <a href="/img/revistas/img1.jpg"/>
            <a href="http://www.scielo.br/abc/img2.jpg"/>
            <a href="/revistas/img3.jpg"/>
            <a href="http://www.scielo.org/local/Image/scielo20_pt.png"/>'''

        self.page.migrate_urls()

        results = [item['href'] for item in self.page.files]
        expected_items = [
             '/img/revistas/img1.jpg',
             '/abc/img2.jpg',
             '/revistas/img3.jpg',
             'http://www.scielo.org/local/Image/scielo20_pt.png'
            ]
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
        self.assertEqual(results, expected_items)

    def test_guess_file_location_img_revistas(self):
        expected = 'htdocs/img/revistas/abc.jpg'
        text = self.page.guess_file_location(
            'www.scielo.br/img/revistas/abc.jpg'
        )
        self.assertEqual(text, expected)

    def test_guess_file_location_revistas(self):
        expected = 'htdocs/revistas/abc.jpg'
        text = self.page.guess_file_location(
            'wwww.scielo.br/revistas/abc.jpg'
        )
        self.assertEqual(text, expected)

    def test_guess_file_location_page(self):
        expected = 'htdocs/abc/abc.jpg'
        text = self.page.guess_file_location('www.scielo.br/abc/abc.jpg')
        self.assertEqual(text, expected)

    def test_guess_file_location_page_relative(self):
        expected = 'htdocs/abc/abc.jpg'
        text = self.page.guess_file_location('/abc/abc.jpg')
        self.assertEqual(text, expected)

    def test_get_prefixed_slug_name(self):
        expected = 'criterios_es_criterio-brasil.jpg'
        ret = self.page.get_prefixed_slug_name('/abc/abc/Critério_Brasil.jpg')
        self.assertEqual(ret, expected)

    @patch.object(Page, 'confirm_file_location')
    def test_get_file_info_img1(self, mocked_confirm_file_location):
        mocked_confirm_file_location.return_value = True
        result = self.page.get_file_info('/img/revistas/img1.jpg')
        img_location = os.path.join(IMG_REVISTAS_PATH, 'img1.jpg')
        img_dest_name = 'criterios_es_img1.jpg'
        self.assertEqual(result, (img_location, img_dest_name))

    @patch.object(Page, 'confirm_file_location')
    def test_get_file_info_img2(self, mocked_confirm_file_location):
        mocked_confirm_file_location.return_value = True
        result = self.page.get_file_info('/abc/img2.jpg')
        img_location = os.path.join(HTDOCS, 'abc/img2.jpg')
        img_dest_name = 'criterios_es_img2.jpg'
        self.assertEqual(result, (img_location, img_dest_name))

    @patch.object(Page, 'confirm_file_location')
    @patch.object(Page, '_register_image')
    def test_create_images(self,
                           mocked_register_image,
                           mocked_confirm_file_location):
        self.page.content = '''
            <img src="/img/revistas/img1.jpg"/>
            <img src="http://www.scielo.br/abc/img2.jpg"/>
            <img src="/revistas/img3.jpg"/>
            <img src="http://www.scielo.org/local/Image/scielo20_pt.png"/>'''
        mocked_register_image.side_effect = [
            '/media/criterios_es_img1.jpg',
            '/media/criterios_es_img2.jpg',
            '/media/criterios_es_img3.jpg',
            ]
        mocked_confirm_file_location.return_value = True
        self.page.create_images()

        results = [img['src'] for img in self.page.images]
        expected_items = [
             '/media/criterios_es_img1.jpg',
             '/media/criterios_es_img2.jpg',
             '/media/criterios_es_img3.jpg',
             'http://www.scielo.org/local/Image/scielo20_pt.png'
            ]
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
        self.assertEqual(results, expected_items)

    @patch.object(Page, 'confirm_file_location')
    @patch.object(Page, '_register_file')
    def test_create_files(self,
                           mocked_register_file,
                           mocked_confirm_file_location):
        self.page.content = '''
            <a href="/img/revistas/img1.jpg"/>
            <a href="http://www.scielo.br/abc/img2.jpg"/>
            <a href="/revistas/img3.jpg"/>
            <a href="http://www.scielo.org/local/Image/scielo20_pt.png"/>'''
        mocked_register_file.side_effect = [
            '/media/criterios_es_img1.jpg',
            '/media/criterios_es_img2.jpg',
            '/media/criterios_es_img3.jpg',
            ]
        mocked_confirm_file_location.return_value = True
        self.page.create_files()

        results = [item['href'] for item in self.page.files]
        expected_items = [
             '/media/criterios_es_img1.jpg',
             '/media/criterios_es_img2.jpg',
             '/media/criterios_es_img3.jpg',
             'http://www.scielo.org/local/Image/scielo20_pt.png'
            ]
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
        self.assertEqual(results, expected_items)


class UtilsJournalPageTestCase(BaseTestCase):

    def setUp(self):
        content = ''
        original_website = 'http://www.scielo.br'
        revistas_path = REVISTAS_PATH
        img_revistas_path = IMG_REVISTAS_PATH
        static_files_path = HTDOCS
        self.page = JournalPage(content, original_website, revistas_path,
                                img_revistas_path, 'abcd', static_files_path)

    def test_original_journal_home_page(self):
        self.assertEqual(
            self.page.original_journal_home_page, 'www.scielo.br/abcd')

    def test_new_journal_home_page(self):
        self.assertEqual(
            self.page.new_journal_home_page, '/journal/abcd/')

    def test_new_about_journal_page(self):
        self.assertEqual(
            self.page.new_about_journal_page('about'),
            '/journal/abcd/about/#about')

    def test_new_about_journal_page_not_anchor(self):
        self.assertEqual(
            self.page.new_about_journal_page('not-anchor'),
            '/journal/abcd/about')

    def test_get_new_url_journal(self):
        # www.scielo.br/icse -> /journal/icse/
        self.assertEqual(
            self.page.get_new_url(
                'https://www.scielo.br/abcd'),
            '/journal/abcd/')

    def test_get_new_url_journal_about(self):
        # www.scielo.br/revistas/icse/iaboutj.htm -> /journal/icse/about/#about
        self.assertEqual(
            self.page.get_new_url('www.scielo.br/revistas/abcd/iaboutj.htm'),
            '/journal/abcd/about/#about')

    def test_get_new_url_journal_instruct(self):
        # www.scielo.br/revistas/icse/iinstruct.htm
        # -> /journal/icse/about/#instructions
        self.assertEqual(
            self.page.get_new_url('www.scielo.br/revistas/abcd/iinstruct.htm'),
            '/journal/abcd/about/#instructions')

    def test_get_new_url_journal_edboard(self):
        # www.scielo.br/revistas/icse/iedboard.htm
        # -> /journal/icse/about/#editors
        self.assertEqual(
            self.page.get_new_url('www.scielo.br/revistas/abcd/iedboard.htm'),
            '/journal/abcd/about/#editors')
