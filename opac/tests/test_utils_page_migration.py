# coding: utf-8

import os
from unittest.mock import Mock, patch

from webapp.utils import page_migration
from webapp.utils import utils as wutils
from webapp.utils.page_migration import (
    JournalPageMigration,
    MigratedPage,
    PageMigration,
    new_author_url_page,
)

from .base import BaseTestCase

REVISTAS_PATH = "htdocs/revistas"
IMG_REVISTAS_PATH = "htdocs/img/revistas"
HTDOCS = "htdocs"


TESTS_REVISTAS_PATH = "opac/tests/fixtures/pages/revistas"
TESTS_IMG_REVISTAS_PATH = "opac/tests/fixtures/pages/img_revistas"


class UtilsJournalMigratedPageTestCase(BaseTestCase):
    def setUp(self):
        original_website = "http://www.scielo.br"
        revistas_path = REVISTAS_PATH
        img_revistas_path = IMG_REVISTAS_PATH
        static_files_path = HTDOCS
        self.migration = PageMigration(
            original_website, revistas_path, img_revistas_path, static_files_path
        )
        self.page = MigratedPage(self.migration, "", acron="acron", lang="es")

    def test_content(self):
        self.page.content = """<html><body><a href="acron.jpg"/>
            <a href="www.scielo.br/jxabc.png"/>
            <a href="user@email.org"/>
            <a href="www.site.org"/>
            <a href="xyz.txt"/>
            </body></html>"""
        self.assertIn("/revistas/acron/acron.jpg", self.page.content)
        self.assertIn('"user@email.org"', self.page.content)
        self.assertIn('"www.site.org"', self.page.content)
        self.assertIn('"xyz.txt"', self.page.content)
        self.assertIn('"www.scielo.br/jxabc.png"', self.page.content)

        self.page.fix_urls()
        self.assertIn('"/jxabc.png"', self.page.content)


class UtilsPageMigration_TestCase(BaseTestCase):
    def test_new_author(self):
        old = (
            "http://www.scielo.br/cgi-bin/wxis.exe/iah/"
            + "?IsisScript=iah/iah.xis&"
            + "base=article%5Edlibrary&format=iso.pft&lang=p&"
            + "nextAction=lnk&"
            + "indexSearch=AU&exprSearch=MEIERHOFFER,+LILIAN+KOZSLOWSKI"
        )
        new = "//search.scielo.org/?q=au:MEIERHOFFER,+LILIAN+KOZSLOWSKI"
        self.assertEqual(new, new_author_url_page(old))

    @patch("requests.get")
    def test_downloaded_file(self, mocked_requests_get):
        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b"content"
        mocked_requests_get.return_value = mocked_response
        f = page_migration.downloaded_file("https://bla/bla.pdf")
        self.assertEqual(open(f, "rb").read(), mocked_response.content)
        os.remove(f)


class UtilsPageMigrationTestCase(BaseTestCase):
    def setUp(self):
        original_website = "http://www.scielo.br"
        revistas_path = REVISTAS_PATH
        img_revistas_path = IMG_REVISTAS_PATH
        static_files_path = HTDOCS
        self.migration = PageMigration(
            original_website, revistas_path, img_revistas_path, static_files_path
        )

    def test_original_web_site(self):
        self.assertEqual(self.migration.original_website, "www.scielo.br")

    def test_replace_by_relative_url_pdf(self):
        old = "www.scielo.br/revistas/icse/levels.pdf"
        new = "/revistas/icse/levels.pdf"
        self.assertEqual(new, self.migration.replace_by_relative_url(old))

    def test_replace_by_relative_url_pdf_img_revistas(self):
        old = "www.scielo.br/img/revistas/icse/levels.pdf"
        new = "/img/revistas/icse/levels.pdf"
        self.assertEqual(new, self.migration.replace_by_relative_url(old))

    def test_replace_by_relative_url(self):
        old = "http://www.scielo.br"
        new = "/"
        self.assertEqual(new, self.migration.replace_by_relative_url(old))

    def test_replace_by_relative_url_any_image(self):
        old = "http://www.scielo.br/abc/img2.jpg"
        new = "/abc/img2.jpg"
        self.assertEqual(new, self.migration.replace_by_relative_url(old))

    def test_replace_by_relative_url_scielo_php(self):
        old = "http://www.scielo.br/scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso"
        new = "/scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso"
        self.assertEqual(new, self.migration.replace_by_relative_url(old))

    def test_link_display_text_1(self):
        expected = "www.scielo.br/revistas/icse/levels.pdf"
        text = self.migration.link_display_text(
            "/revistas/icse/levels.pdf",
            "www.scielo.br/revistas/icse/levels.pdf",
            "www.scielo.br/revistas/icse/levels.pdf",
        )
        self.assertEqual(text, expected)

    def test_link_display_text_2(self):
        expected = "www.scielo.br/img/revistas/icse/levels.pdf"
        text = self.migration.link_display_text(
            "/img/revistas/icse/levels.pdf",
            "www.scielo.br/img/revistas/icse/levels.pdf",
            "www.scielo.br/img/revistas/icse/levels.pdf",
        )
        self.assertEqual(text, expected)

    def test_link_display_text_3(self):
        expected = "www.scielo.br/journal/icse/about/#instructions"
        text = self.migration.link_display_text(
            "/journal/icse/about/#instructions",
            "www.scielo.br/revistas/icse/iinstruc.htm",
            "www.scielo.br/revistas/icse/iinstruc.htm",
        )
        self.assertEqual(text, expected)

    def test_link_display_text_4(self):
        expected = "www.scielo.br"
        text = self.migration.link_display_text("/", "www.scielo.br", "www.scielo.br ")
        self.assertEqual(text, expected)

    def test_get_possible_locations_img_revistas(self):
        expected = "htdocs/img/revistas/abc.jpg"
        expected_items = ["htdocs/img/revistas/abc.jpg"]
        result = self.migration.get_possible_locations(
            "www.scielo.br/img/revistas/abc.jpg"
        )
        self.assertIn(expected, result)
        self.assertEqual(set(expected_items), set(result))

    def test_get_possible_locations_revistas(self):
        expected = "htdocs/revistas/abc.jpg"
        expected_items = ["htdocs/revistas/abc.jpg"]
        result = self.migration.get_possible_locations("www.scielo.br/revistas/abc.jpg")
        self.assertIn(expected, result)
        self.assertEqual(set(expected_items), set(result))

    def test_get_possible_locations_page(self):
        expected = "htdocs/abc/abc.jpg"
        expected_items = ["htdocs/abc/abc.jpg"]
        result = self.migration.get_possible_locations("www.scielo.br/abc/abc.jpg")
        self.assertIn(expected, result)
        self.assertEqual(set(expected_items), set(result))

    def test_get_possible_locations_page_relative(self):
        expected = "htdocs/abc/abc.jpg"
        expected_items = [
            "htdocs/abc/abc.jpg",
        ]
        result = self.migration.get_possible_locations("/abc/abc.jpg")
        self.assertIn(expected, result)
        self.assertEqual(set(expected_items), set(result))

    def test_get_possible_locations_page_relative_2(self):
        expected = "htdocs/abc.jpg"
        expected_items = [
            "htdocs/img/revistas/abc.jpg",
            "htdocs/revistas/abc.jpg",
            "htdocs/abc.jpg",
        ]
        result = self.migration.get_possible_locations("abc.jpg")
        self.assertIn(expected, result)
        self.assertEqual(set(expected_items), set(result))


class UtilsMigratedPageTestCase(BaseTestCase):
    def setUp(self):
        original_website = "http://www.scielo.br"
        revistas_path = REVISTAS_PATH
        img_revistas_path = IMG_REVISTAS_PATH
        static_files_path = HTDOCS
        self.migration = PageMigration(
            original_website, revistas_path, img_revistas_path, static_files_path
        )
        self.page = MigratedPage(
            self.migration, "", acron="abc", page_name="criterio", lang="es"
        )

    def test_content(self):
        self.page.content = "<html><body>x</body></html>"
        self.assertEqual(self.page.content, "x")

    def test_find_old_website_uri_items(self):
        self.page.content = """<img src="http://www.scielo.br"/>
                            <img src="http://www.scielo.br/abc"/>
                            <img src="/img/revistas/abc.jpg"/>
                            <img src="http://www.scielo.br/abc/iaboutj.htm"/>
                            <img src="http://scielo.br/img/revistas"/>"""

        result = list(self.page.find_old_website_uri_items("img", "src"))
        self.assertEqual(result[0]["src"], "http://www.scielo.br")
        self.assertEqual(result[1]["src"], "http://www.scielo.br/abc")
        self.assertEqual(result[2]["src"], "/img/revistas/abc.jpg")
        self.assertEqual(result[3]["src"], "http://www.scielo.br/abc/iaboutj.htm")
        self.assertEqual(len(result), 4)

    def test_fix_urls(self):
        self.page.content = """
            <img src="/img/revistas/img1.jpg"/>
            <img src="http://www.scielo.br/abc/img2.jpg"/>
            <img src="/revistas/img3.jpg"/>
            <img src="http://www.scielo.org/local/Image/scielo20_pt.png"/>"""

        self.page.fix_urls()

        results = [img["src"] for img in self.page.images]
        expected_items = [
            "/img/revistas/img1.jpg",
            "/abc/img2.jpg",
            "/revistas/img3.jpg",
            "http://www.scielo.org/local/Image/scielo20_pt.png",
        ]
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
        self.assertEqual(results, expected_items)

    def test_fix_urls_2(self):
        self.page.content = """
            <a href="/journal/abmvz/"/>
        """
        self.page.fix_urls()

        results = [item["href"] for item in self.page.files]
        expected_items = []
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
        self.assertEqual(results, expected_items)

    def test_fix_urls_files(self):
        self.page.content = """
            <a href="/img/revistas/img1.jpg"/>
            <a href="http://www.scielo.br/abc/img2.jpg"/>
            <a href="/revistas/img3.jpg"/>
            <a href="http://www.scielo.org/local/Image/scielo20_pt.png"/>"""
        self.page.fix_urls()
        results = [item["href"] for item in self.page.files]
        expected_items = [
            "/img/revistas/img1.jpg",
            "/abc/img2.jpg",
            "/revistas/img3.jpg",
            "http://www.scielo.org/local/Image/scielo20_pt.png",
        ]
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
        self.assertEqual(results, expected_items)

    def test_get_prefixed_slug_name(self):
        expected = "criterio_es_criterio-brasil.jpg"
        ret = self.page.get_prefixed_slug_name("/abc/abc/Critério_Brasil.jpg")
        self.assertEqual(ret, expected)

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(page_migration, "confirm_file_location", return_value=True)
    def test_get_file_info_img1(self, mocked_confirm_file_location, mocked_isfile):
        self.page.prefixes = ["criterios", "es"]
        result = self.page.get_file_info("/img/revistas/img1.jpg")
        img_location = os.path.join(IMG_REVISTAS_PATH, "img1.jpg")
        img_dest_name = "criterios_es_img1.jpg"
        self.assertEqual(result, (img_location, img_dest_name, False))

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(page_migration, "confirm_file_location", return_value=True)
    def test_get_file_info_img2(self, mocked_confirm_file_location, mocked_isfile):
        self.page.prefixes = ["criterios", "es"]
        result = self.page.get_file_info("/abc/img2.jpg")
        img_location = os.path.join(HTDOCS, "abc/img2.jpg")
        img_dest_name = "criterios_es_img2.jpg"
        self.assertEqual(result, (img_location, img_dest_name, False))

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(page_migration, "confirm_file_location", return_value=True)
    @patch.object(wutils, "migrate_page_create_image")
    def test_create_images_from_local_files(
        self, mocked_create_image_function, mocked_confirm_file_location, mocked_isfile
    ):
        self.page.content = """
            <img src="/img/revistas/img1.jpg"/>
            <img src="http://www.scielo.br/abc/img2.jpg"/>
            <img src="/revistas/img3.jpg"/>
            <img src="http://www.scielo.org/local/Image/scielo20_pt.png"/>"""

        mocked_confirm_file_location.side_effect = [True, True, True]
        mocked_create_image_function.side_effect = [
            "/media/criterios_es_img1.jpg",
            "/media/criterios_es_img2.jpg",
            "/media/criterios_es_img3.jpg",
        ]
        self.page.fix_urls()
        self.page.create_images(mocked_create_image_function)

        results = [img["src"] for img in self.page.images]
        expected_items = [
            "/media/criterios_es_img1.jpg",
            "/media/criterios_es_img2.jpg",
            "/media/criterios_es_img3.jpg",
            "http://www.scielo.org/local/Image/scielo20_pt.png",
        ]
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
        self.assertEqual(results, expected_items)

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(page_migration, "confirm_file_location")
    @patch.object(wutils, "migrate_page_create_file")
    def test_create_files_from_local_file(
        self, mocked_create_file_function, mocked_confirm_file_location, mocked_isfile
    ):
        self.page.content = """
            <a href="/img/revistas/img1.jpg"/>
        """
        mocked_confirm_file_location.side_effect = [
            True,
        ]
        mocked_create_file_function.side_effect = [
            "/media/criterios_es_img1.jpg",
        ]

        files = list(self.page.files)
        self.assertEqual(files[0]["href"], "/img/revistas/img1.jpg")
        file_locations = self.page.migration.get_possible_locations(
            "/img/revistas/img1.jpg"
        )
        self.assertEqual(
            file_locations, ["{}/{}".format(IMG_REVISTAS_PATH, "img1.jpg")]
        )

        self.page.create_files(mocked_create_file_function)

        results = [item["href"] for item in self.page.files]
        expected_items = [
            "/media/criterios_es_img1.jpg",
        ]
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
        self.assertEqual(results, expected_items)

    @patch.object(os.path, "isfile", return_value=True)
    @patch.object(page_migration, "confirm_file_location", return_value=True)
    @patch.object(wutils, "migrate_page_create_file")
    def test_create_files_from_local_files(
        self, mocked_create_file_function, mocked_confirm_file_location, mocked_isfile
    ):
        self.page.content = """
            <a href="/img/revistas/img1.jpg"/>
            <a href="http://www.scielo.br/abc/img2.jpg"/>
            <a href="/revistas/img3.jpg"/>
            <a href="http://www.scielo.org/local/Image/scielo20_pt.png"/>"""
        mocked_create_file_function.side_effect = [
            "/media/criterios_es_img1.jpg",
            "/media/criterios_es_img2.jpg",
            "/media/criterios_es_img3.jpg",
        ]
        self.page.fix_urls()
        self.page.create_files(mocked_create_file_function)

        results = [item["href"] for item in self.page.files]
        expected_items = [
            "/media/criterios_es_img1.jpg",
            "/media/criterios_es_img2.jpg",
            "/media/criterios_es_img3.jpg",
            "http://www.scielo.org/local/Image/scielo20_pt.png",
        ]
        self.assertEqual(results, expected_items)
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)

    @patch("webapp.utils.page_migration.downloaded_file")
    @patch("webapp.utils.page_migration.confirm_file_location")
    @patch.object(wutils, "migrate_page_create_image")
    def test_create_images_from_downloaded_files(
        self, mocked_create_item, mocked_confirm_file_location, mocked_downloaded_file
    ):
        self.page.content = """
            <img src="/img/revistas/img1.jpg"/>
            <img src="http://www.scielo.br/abc/img2.jpg"/>
            <img src="/revistas/img3.jpg"/>
            <img src="http://www.scielo.org/local/Image/scielo20_pt.png"/>"""
        mocked_create_item.side_effect = [
            "/media/criterios_es_img1.jpg",
            "/media/criterios_es_img2.jpg",
            "/media/criterios_es_img3.jpg",
        ]
        mocked_downloaded_file.side_effect = [
            "/tmp/img1.jpg",
            "/tmp/img2.jpg",
            "/tmp/img3.jpg",
        ]
        mocked_confirm_file_location.side_effect = [
            False,
            True,
            False,
            True,
            False,
            True,
        ]
        self.page.fix_urls()
        self.page.create_images(mocked_create_item)

        results = [img["src"] for img in self.page.images]
        expected_items = [
            "/media/criterios_es_img1.jpg",
            "/media/criterios_es_img2.jpg",
            "/media/criterios_es_img3.jpg",
            "http://www.scielo.org/local/Image/scielo20_pt.png",
        ]
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
        self.assertEqual(results, expected_items)

    @patch.object(page_migration, "downloaded_file")
    @patch.object(page_migration, "confirm_file_location")
    @patch.object(wutils, "migrate_page_create_file")
    def test_create_files_from_downloaded_files(
        self,
        mocked_create_file_function,
        mocked_confirm_file_location,
        mocked_downloaded_file,
    ):
        self.page.content = """
            <a href="/img/revistas/img1.jpg"/>
            <a href="http://www.scielo.br/abc/img2.jpg"/>
            <a href="/revistas/img3.jpg"/>
            <a href="http://www.scielo.org/local/Image/scielo20_pt.png"/>"""
        mocked_create_file_function.side_effect = [
            "/media/criterios_es_img1.jpg",
            "/media/criterios_es_img2.jpg",
            "/media/criterios_es_img3.jpg",
        ]
        mocked_downloaded_file.side_effect = [
            "/tmp/img1.jpg",
            "/tmp/img2.jpg",
            "/tmp/img3.jpg",
        ]
        mocked_confirm_file_location.side_effect = [
            False,
            True,
            False,
            True,
            False,
            True,
        ]
        self.page.fix_urls()
        self.page.create_files(mocked_create_file_function)

        results = [item["href"] for item in self.page.files]
        expected_items = [
            "/media/criterios_es_img1.jpg",
            "/media/criterios_es_img2.jpg",
            "/media/criterios_es_img3.jpg",
            "http://www.scielo.org/local/Image/scielo20_pt.png",
        ]
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
        self.assertEqual(results, expected_items)

    @patch.object(page_migration, "downloaded_file", side_effect=None)
    @patch.object(page_migration, "confirm_file_location", side_effect=[False, False])
    @patch.object(wutils, "migrate_page_create_file")
    @patch.object(page_migration, "logging")
    def test_create_files_failure(
        self,
        mock_logger,
        mocked_create_file_function,
        mocked_confirm_file_location,
        mocked_downloaded_file,
    ):
        self.page.content = """<a href="/img/revistas/img1.jpg"/>"""
        self.page.fix_urls()
        self.page.create_files(mocked_create_file_function)
        mock_logger.info.assert_called_with(
            "CONFERIR: /img/revistas/img1.jpg não encontrado"
        )


class UtilsJournalPageMigrationTestCase(BaseTestCase):
    def setUp(self):
        original_website = "http://www.scielo.br"
        self.jmigr = JournalPageMigration(original_website, "abcd")

    def test_original_journal_home_page(self):
        self.assertEqual(self.jmigr.original_journal_home_page, "www.scielo.br/abcd")

    def test_new_journal_home_page(self):
        self.assertEqual(self.jmigr.new_journal_home_page, "/journal/abcd/")

    def test_new_about_journal_page(self):
        self.assertEqual(
            self.jmigr.new_about_journal_page("about"), "/journal/abcd/about/#about"
        )

    def test_new_about_journal_page_not_anchor(self):
        self.assertEqual(
            self.jmigr.new_about_journal_page("not-anchor"), "/journal/abcd/about"
        )

    def test_get_new_url_journal(self):
        # www.scielo.br/icse -> /journal/icse/
        self.assertEqual(
            self.jmigr.get_new_url("https://www.scielo.br/abcd"), "/journal/abcd/"
        )

    def test_get_new_url_journal_about(self):
        # www.scielo.br/revistas/icse/iaboutj.htm -> /journal/icse/about/#about
        self.assertEqual(
            self.jmigr.get_new_url("www.scielo.br/revistas/abcd/iaboutj.htm"),
            "/journal/abcd/about/#about",
        )

    def test_get_new_url_journal_instruct(self):
        # www.scielo.br/revistas/icse/iinstruct.htm
        # -> /journal/icse/about/#instructions
        self.assertEqual(
            self.jmigr.get_new_url("www.scielo.br/revistas/abcd/iinstruct.htm"),
            "/journal/abcd/about/#instructions",
        )

    def test_get_new_url_journal_edboard(self):
        # www.scielo.br/revistas/icse/iedboard.htm
        # -> /journal/icse/about/#editors
        self.assertEqual(
            self.jmigr.get_new_url("www.scielo.br/revistas/abcd/iedboard.htm"),
            "/journal/abcd/about/#editors",
        )


class UtilsMigratedJournalPageTestCase(BaseTestCase):
    def setUp(self):
        original_website = "http://www.scielo.br"
        self.revistas_path = TESTS_REVISTAS_PATH
        self.img_revistas_path = TESTS_IMG_REVISTAS_PATH
        self.static_files_path = None
        self.migration = PageMigration(
            original_website,
            self.revistas_path,
            self.img_revistas_path,
            self.static_files_path,
        )
        self.page = MigratedPage(self.migration, "", acron="aa", lang="es")

    @patch.object(wutils, "migrate_page_create_file")
    def test_create_files(self, mocked_create_file_function):
        pdf_file_path = "PASSO A PASSO – SISTEMA DE SUBMISSÃO DE ARTIGOS POR INTERMÉDIO DO SCHOLARONE.pdf"
        self.page.content = '<a href="{}"/>'.format(pdf_file_path)
        self.assertIn("/revistas/aa/{}".format(pdf_file_path), self.page.content)

        for a in self.page.files:
            result = self.migration.get_possible_locations(a["href"])
            self.assertIn("{}/aa/{}".format(TESTS_REVISTAS_PATH, pdf_file_path), result)

        mocked_create_file_function.side_effect = [
            "/media/files/aa_passo-a-passo-sistema-de-submissao-de-artigos-por-intermedio-do-scholarone.pdf",
        ]
        _file_info = self.page.get_file_info(list(self.page.files)[0]["href"])

        file_info = (
            "opac/tests/fixtures/pages/revistas/aa/PASSO A PASSO – SISTEMA DE SUBMISSÃO DE ARTIGOS POR INTERMÉDIO DO SCHOLARONE.pdf",
            "aa_passo-a-passo-sistema-de-submissao-de-artigos-por-intermedio-do-scholarone.pdf",
            False,
        )
        self.assertEqual(file_info, _file_info)
        self.page.create_files(mocked_create_file_function)
        results = [item["href"] for item in self.page.files]
        expected_items = [
            "/media/files/aa_passo-a-passo-sistema-de-submissao-de-artigos-por-intermedio-do-scholarone.pdf",
        ]
        expected = pdf_file_path
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)


class UtilsMigratedABMVZJournalPageTestCase(BaseTestCase):
    def create_item(self, source, dest, check_if_exists=False):
        return ""

    def setUp(self):
        original_website = "http://www.scielo.br"
        self.revistas_path = TESTS_REVISTAS_PATH
        self.img_revistas_path = TESTS_IMG_REVISTAS_PATH
        self.static_files_path = None
        create_image = self.create_item
        create_file = self.create_item
        self.migration = PageMigration(
            original_website,
            self.revistas_path,
            self.img_revistas_path,
            self.static_files_path,
        )
        self.page = MigratedPage(self.migration, "", acron="abmvz", lang="es")

    @patch("requests.get")
    @patch.object(wutils, "migrate_page_create_file")
    def test_create_files_from_downloaded_files(
        self,
        mocked_create_file_function,
        mocked_requests_get,
    ):
        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b"content"
        mocked_requests_get.return_value = mocked_response

        pdf_file_path = "PASSO A PASSO – SISTEMA DE SUBMISSÃO DE ARTIGOS POR INTERMÉDIO DO SCHOLARONE.pdf"
        self.page.content = '<a href="{}"/>'.format(pdf_file_path)
        self.assertIn("/revistas/abmvz/{}".format(pdf_file_path), self.page.content)

        files = list(self.page.files)
        result = self.migration.get_possible_locations(files[0]["href"])
        self.assertIn("{}/abmvz/{}".format(TESTS_REVISTAS_PATH, pdf_file_path), result)

        mocked_create_file_function.side_effect = [
            "/media/files/abmvz_passo-a-passo-sistema-de-submissao-de-artigos-por-intermedio-do-scholarone.pdf",
        ]
        _file_info = self.page.get_file_info(files[0]["href"])
        file_info = (
            "/tmp/tmpcjnmoyos/PASSO A PASSO – SISTEMA DE SUBMISSÃO DE ARTIGOS POR INTERMÉDIO DO SCHOLARONE.pdf",
            "abmvz_passo-a-passo-sistema-de-submissao-de-artigos-por-intermedio-do-scholarone.pdf",
            True,
        )
        self.assertEqual(file_info[1], _file_info[1])
        self.assertEqual(file_info[2], _file_info[2])

        self.page.create_files(mocked_create_file_function)
        results = [item["href"] for item in self.page.files]
        expected_items = [
            "/media/files/abmvz_passo-a-passo-sistema-de-submissao-de-artigos-por-intermedio-do-scholarone.pdf",
        ]
        expected = pdf_file_path
        for result, expected in zip(results, expected_items):
            self.assertEqual(result, expected)
