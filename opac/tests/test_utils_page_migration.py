# coding: utf-8

import os
from .base import BaseTestCase

from unittest.mock import patch, Mock
from webapp.utils import page_migration
from webapp.utils.page_migration import (
    MigratedPage, PageMigration, JournalPageMigration, new_author_url_page
)


REVISTAS_PATH = 'htdocs/revistas'
IMG_REVISTAS_PATH = 'htdocs/img/revistas'
HTDOCS = 'htdocs'


class UtilsPageMigration_TestCase(BaseTestCase):

    def test_new_author(self):
        old = 'http://www.scielo.br/cgi-bin/wxis.exe/iah/' + \
              '?IsisScript=iah/iah.xis&' + \
              'base=article%5Edlibrary&format=iso.pft&lang=p&' + \
              'nextAction=lnk&' + \
              'indexSearch=AU&exprSearch=MEIERHOFFER,+LILIAN+KOZSLOWSKI'
        new = '//search.scielo.org/?q=au:MEIERHOFFER,+LILIAN+KOZSLOWSKI'
        self.assertEqual(new, new_author_url_page(old))

    @patch('requests.get')
    def test_downloaded_file(self, mocked_requests_get):
        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b'content'
        mocked_requests_get.return_value = mocked_response
        f = page_migration.downloaded_file('https://bla/bla.pdf')
        self.assertEqual(open(f, 'rb').read(), mocked_response.content)
        os.remove(f)


class UtilsPageMigrationTestCase(BaseTestCase):

    def setUp(self):
        original_website = 'http://www.scielo.br'
        revistas_path = REVISTAS_PATH
        img_revistas_path = IMG_REVISTAS_PATH
        static_files_path = HTDOCS
        create_image = Mock()
        create_file = Mock()
        self.migration = PageMigration(create_image, create_file,
                                       original_website, revistas_path,
                                       img_revistas_path, static_files_path)

    def test_original_web_site(self):
        self.assertEqual(self.migration.original_website, 'www.scielo.br')

    def test_replace_by_relative_url_pdf(self):
        old = 'www.scielo.br/revistas/icse/levels.pdf'
        new = '/revistas/icse/levels.pdf'
        self.assertEqual(new, self.migration.replace_by_relative_url(old))

    def test_replace_by_relative_url_pdf_img_revistas(self):
        old = 'www.scielo.br/img/revistas/icse/levels.pdf'
        new = '/img/revistas/icse/levels.pdf'
        self.assertEqual(new, self.migration.replace_by_relative_url(old))

    def test_replace_by_relative_url(self):
        old = 'http://www.scielo.br'
        new = '/'
        self.assertEqual(new, self.migration.replace_by_relative_url(old))

    def test_replace_by_relative_url_any_image(self):
        old = 'http://www.scielo.br/abc/img2.jpg'
        new = '/abc/img2.jpg'
        self.assertEqual(new, self.migration.replace_by_relative_url(old))

    def test_replace_by_relative_url_scielo_php(self):
        old = 'http://www.scielo.br/scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso'
        new = '/scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso'
        self.assertEqual(new, self.migration.replace_by_relative_url(old))

    def test_link_display_text_1(self):
        expected = 'www.scielo.br/revistas/icse/levels.pdf'
        text = self.migration.link_display_text(
            '/revistas/icse/levels.pdf',
            'www.scielo.br/revistas/icse/levels.pdf',
            'www.scielo.br/revistas/icse/levels.pdf')
        self.assertEqual(text, expected)

    def test_link_display_text_2(self):
        expected = 'www.scielo.br/img/revistas/icse/levels.pdf'
        text = self.migration.link_display_text(
            '/img/revistas/icse/levels.pdf',
            'www.scielo.br/img/revistas/icse/levels.pdf',
            'www.scielo.br/img/revistas/icse/levels.pdf')
        self.assertEqual(text, expected)

    def test_link_display_text_3(self):
        expected = 'www.scielo.br/journal/icse/about/#instructions'
        text = self.migration.link_display_text(
            '/journal/icse/about/#instructions',
            'www.scielo.br/revistas/icse/iinstruc.htm',
            'www.scielo.br/revistas/icse/iinstruc.htm')
        self.assertEqual(text, expected)

    def test_link_display_text_4(self):
        expected = 'www.scielo.br'
        text = self.migration.link_display_text(
            '/',
            'www.scielo.br',
            'www.scielo.br ')
        self.assertEqual(text, expected)

    def test_guess_file_location_img_revistas(self):
        expected = 'htdocs/img/revistas/abc.jpg'
        text = self.migration.guess_file_location(
            'www.scielo.br/img/revistas/abc.jpg'
        )
        self.assertEqual(text, expected)

    def test_guess_file_location_revistas(self):
        expected = 'htdocs/revistas/abc.jpg'
        text = self.migration.guess_file_location(
            'wwww.scielo.br/revistas/abc.jpg'
        )
        self.assertEqual(text, expected)

    def test_guess_file_location_page(self):
        expected = 'htdocs/abc/abc.jpg'
        text = self.migration.guess_file_location('www.scielo.br/abc/abc.jpg')
        self.assertEqual(text, expected)

    def test_guess_file_location_page_relative(self):
        expected = 'htdocs/abc/abc.jpg'
        text = self.migration.guess_file_location('/abc/abc.jpg')
        self.assertEqual(text, expected)

    def test_get_prefixed_slug_name(self):
        expected = 'criterios_es_criterio-brasil.jpg'
        ret = self.migration.get_prefixed_slug_name(
            ['criterios', 'es'], '/abc/abc/Critério_Brasil.jpg')
        self.assertEqual(ret, expected)

    @patch.object(page_migration, 'confirm_file_location', return_value=True)
    def test_get_file_info_img1(self, mocked_confirm_file_location):
        result = self.migration.get_file_info(
            ['criterios', 'es'], '/img/revistas/img1.jpg')
        img_location = os.path.join(IMG_REVISTAS_PATH, 'img1.jpg')
        img_dest_name = 'criterios_es_img1.jpg'
        self.assertEqual(result, (img_location, img_dest_name, False))

    @patch.object(page_migration, 'confirm_file_location', return_value=True)
    def test_get_file_info_img2(self, mocked_confirm_file_location):
        result = self.migration.get_file_info(
            ['criterios', 'es'], '/abc/img2.jpg')
        img_location = os.path.join(HTDOCS, 'abc/img2.jpg')
        img_dest_name = 'criterios_es_img2.jpg'
        self.assertEqual(result, (img_location, img_dest_name, False))


class UtilsMigratedPageTestCase(BaseTestCase):

    def create_item(self, source, dest, check_if_exists=False):
        return ''

    def setUp(self):
        original_website = 'http://www.scielo.br'
        revistas_path = REVISTAS_PATH
        img_revistas_path = IMG_REVISTAS_PATH
        static_files_path = HTDOCS
        create_image = self.create_item
        create_file = self.create_item
        migration = PageMigration(create_image, create_file,
                                  original_website, revistas_path,
                                  img_revistas_path, static_files_path)
        self.page = MigratedPage(
                 migration, '',
                 acron=None, page_name='criterio', lang='es')

    def test_content(self):
        self.page.content = '<html><body>x</body></html>'
        self.assertEqual(self.page.content, '<html><body>x</body></html>')

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

    def test_fix_urls(self):
        self.page.content = '''
            <img src="/img/revistas/img1.jpg"/>
            <img src="http://www.scielo.br/abc/img2.jpg"/>
            <img src="/revistas/img3.jpg"/>
            <img src="http://www.scielo.org/local/Image/scielo20_pt.png"/>'''

        self.page.fix_urls()

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

    def test_fix_urls_files(self):
        self.page.content = '''
            <a href="/img/revistas/img1.jpg"/>
            <a href="http://www.scielo.br/abc/img2.jpg"/>
            <a href="/revistas/img3.jpg"/>
            <a href="http://www.scielo.org/local/Image/scielo20_pt.png"/>'''

        self.page.fix_urls()

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

    @patch.object(page_migration, 'confirm_file_location', return_value=True)
    @patch.object(PageMigration, 'create_image_function')
    def test_create_images_from_local_files(self,
                                            mocked_create_image_function,
                                            mocked_confirm_file_location):
        self.page.content = '''
            <img src="/img/revistas/img1.jpg"/>
            <img src="http://www.scielo.br/abc/img2.jpg"/>
            <img src="/revistas/img3.jpg"/>
            <img src="http://www.scielo.org/local/Image/scielo20_pt.png"/>'''

        mocked_create_image_function.side_effect = [
            '/media/criterios_es_img1.jpg',
            '/media/criterios_es_img2.jpg',
            '/media/criterios_es_img3.jpg',
            ]
        self.page.fix_urls()
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

    @patch.object(page_migration, 'confirm_file_location', return_value=True)
    @patch.object(PageMigration, 'create_file_function')
    def test_create_files_from_local_files(self,
                                           mocked_create_image_function,
                                           mocked_confirm_file_location):
        self.page.content = '''
            <a href="/img/revistas/img1.jpg"/>
            <a href="http://www.scielo.br/abc/img2.jpg"/>
            <a href="/revistas/img3.jpg"/>
            <a href="http://www.scielo.org/local/Image/scielo20_pt.png"/>'''
        mocked_create_image_function.side_effect = [
            '/media/criterios_es_img1.jpg',
            '/media/criterios_es_img2.jpg',
            '/media/criterios_es_img3.jpg',
            ]
        self.page.fix_urls()
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

    @patch.object(page_migration, 'downloaded_file')
    @patch.object(page_migration, 'confirm_file_location')
    @patch.object(PageMigration, 'create_image_function')
    def test_create_images_from_downloaded_files(self,
                           mocked_create_item,
                           mocked_confirm_file_location,
                           mocked_downloaded_file):
        self.page.content = '''
            <img src="/img/revistas/img1.jpg"/>
            <img src="http://www.scielo.br/abc/img2.jpg"/>
            <img src="/revistas/img3.jpg"/>
            <img src="http://www.scielo.org/local/Image/scielo20_pt.png"/>'''
        mocked_create_item.side_effect = [
            '/media/criterios_es_img1.jpg',
            '/media/criterios_es_img2.jpg',
            '/media/criterios_es_img3.jpg',
            ]
        mocked_downloaded_file.side_effect = [
            '/tmp/img1.jpg',
            '/tmp/img2.jpg',
            '/tmp/img3.jpg',
            ]
        mocked_confirm_file_location.side_effect = [
            False, True, False, True, False, True
        ]
        self.page.fix_urls()
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

    @patch.object(page_migration, 'downloaded_file')
    @patch.object(page_migration, 'confirm_file_location')
    @patch.object(PageMigration, 'create_file_function')
    def test_create_files_from_downloaded_files(self,
                           mocked_create_file_function,
                           mocked_confirm_file_location,
                           mocked_downloaded_file):
        self.page.content = '''
            <a href="/img/revistas/img1.jpg"/>
            <a href="http://www.scielo.br/abc/img2.jpg"/>
            <a href="/revistas/img3.jpg"/>
            <a href="http://www.scielo.org/local/Image/scielo20_pt.png"/>'''
        mocked_create_file_function.side_effect = [
            '/media/criterios_es_img1.jpg',
            '/media/criterios_es_img2.jpg',
            '/media/criterios_es_img3.jpg',
            ]
        mocked_downloaded_file.side_effect = [
            '/tmp/img1.jpg',
            '/tmp/img2.jpg',
            '/tmp/img3.jpg',
            ]
        mocked_confirm_file_location.side_effect = [
            False, True, False, True, False, True
        ]
        self.page.fix_urls()
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

    @patch.object(page_migration, 'downloaded_file', side_effect=None)
    @patch.object(page_migration, 'confirm_file_location', side_effect=[False, False])
    @patch.object(page_migration, 'logging')
    def test_create_files_failure(self, mock_logger,
                           mocked_confirm_file_location,
                           mocked_downloaded_file):
        self.page.content = '''<a href="/img/revistas/img1.jpg"/>'''
        self.page.fix_urls()
        self.page.create_files()
        mock_logger.info.assert_called_with(
            "CONFERIR: /img/revistas/img1.jpg não encontrado")


class UtilsJournalPageMigrationTestCase(BaseTestCase):

    def setUp(self):
        original_website = 'http://www.scielo.br'
        self.jmigr = JournalPageMigration(original_website, 'abcd')

    def test_original_journal_home_page(self):
        self.assertEqual(
            self.jmigr.original_journal_home_page, 'www.scielo.br/abcd')

    def test_new_journal_home_page(self):
        self.assertEqual(
            self.jmigr.new_journal_home_page, '/journal/abcd/')

    def test_new_about_journal_page(self):
        self.assertEqual(
            self.jmigr.new_about_journal_page('about'),
            '/journal/abcd/about/#about')

    def test_new_about_journal_page_not_anchor(self):
        self.assertEqual(
            self.jmigr.new_about_journal_page('not-anchor'),
            '/journal/abcd/about')

    def test_get_new_url_journal(self):
        # www.scielo.br/icse -> /journal/icse/
        self.assertEqual(
            self.jmigr.get_new_url(
                'https://www.scielo.br/abcd'),
            '/journal/abcd/')

    def test_get_new_url_journal_about(self):
        # www.scielo.br/revistas/icse/iaboutj.htm -> /journal/icse/about/#about
        self.assertEqual(
            self.jmigr.get_new_url('www.scielo.br/revistas/abcd/iaboutj.htm'),
            '/journal/abcd/about/#about')

    def test_get_new_url_journal_instruct(self):
        # www.scielo.br/revistas/icse/iinstruct.htm
        # -> /journal/icse/about/#instructions
        self.assertEqual(
            self.jmigr.get_new_url('www.scielo.br/revistas/abcd/iinstruct.htm'),
            '/journal/abcd/about/#instructions')

    def test_get_new_url_journal_edboard(self):
        # www.scielo.br/revistas/icse/iedboard.htm
        # -> /journal/icse/about/#editors
        self.assertEqual(
            self.jmigr.get_new_url('www.scielo.br/revistas/abcd/iedboard.htm'),
            '/journal/abcd/about/#editors')
