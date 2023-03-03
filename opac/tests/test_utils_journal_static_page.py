# coding: utf-8

import os
import unittest

from flask import current_app, url_for
from webapp.utils.journal_static_page import OldJournalPageFile

from . import utils
from .base import BaseTestCase

REVISTAS_PATH = "opac/tests/fixtures/pages/revistas"
IMG_REVISTAS_PATH = "opac/tests/fixtures/pages/img_revistas"


class OldJournalPageTestCase(BaseTestCase):
    def html_file(self, name):
        f = os.path.join(REVISTAS_PATH, name.replace("_", "/") + ".htm")
        if os.path.isfile(f):
            return f

    def test_title_icse_eaboutj(self):
        jspf = OldJournalPageFile(self.html_file("icse_eaboutj"))
        self.assertEqual(jspf.acron, "icse")
        self.assertEqual(jspf.anchor_title, "<h1>Acerca de la revista</h1>")
        self.assertTrue("<h1>Acerca de la revista</h1>" in jspf.body)

    def test_title_eins_eedboar(self):
        jspf = OldJournalPageFile(self.html_file("eins_eedboard"))
        self.assertEqual(jspf.anchor_title, "<h1>Cuerpo Editorial</h1>")
        self.assertTrue("<h1>Cuerpo Editorial</h1>" in jspf.body)

    def test_title_abb_einstruc(self):
        jspf = OldJournalPageFile(self.html_file("abb_einstruc"))
        self.assertEqual(jspf.anchor_title, "<h1>Instrucciones a los autores</h1>")
        self.assertTrue("<h1>Instrucciones a los autores</h1>" in jspf.body)

    def test_title_bjgeo_einstr(self):
        jspf = OldJournalPageFile(self.html_file("bjgeo_einstruct"))
        self.assertEqual(jspf.anchor_title, "<h1>Instrucciones a los autores</h1>")
        self.assertTrue("<h1>Instrucciones a los autores</h1>" in jspf.body)

    def test_title_bjmbr_pabout(self):
        jspf = OldJournalPageFile(self.html_file("bjmbr_paboutj"))
        self.assertEqual(jspf.anchor_title, "<h1>Sobre o periódico</h1>")
        self.assertTrue("<h1>Sobre o periódico</h1>" in jspf.body)

    def test_title_eagri_pedboa(self):
        jspf = OldJournalPageFile(self.html_file("eagri_pedboard"))
        self.assertEqual(jspf.anchor_title, "<h1>Corpo Editorial</h1>")
        self.assertTrue("<h1>Corpo Editorial</h1>" in jspf.body)

    def test_title_abb_pinstruc(self):
        jspf = OldJournalPageFile(self.html_file("abb_pinstruc"))
        self.assertEqual(jspf.anchor_title, "<h1>Instruções aos autores</h1>")
        self.assertTrue("<h1>Instruções aos autores</h1>" in jspf.body)

    def test_title_bjgeo_pinstr(self):
        jspf = OldJournalPageFile(self.html_file("bjgeo_pinstruct"))
        self.assertEqual(jspf.anchor_title, "<h1>Instruções aos autores</h1>")
        self.assertTrue("<h1>Instruções aos autores</h1>" in jspf.body)

    def test_title_bjmbr_iabout(self):
        jspf = OldJournalPageFile(self.html_file("bjmbr_iaboutj"))
        self.assertEqual(jspf.anchor_title, "<h1>About the journal</h1>")
        self.assertTrue("<h1>About the journal</h1>" in jspf.body)

    def test_title_bjmbr_iedboa(self):
        jspf = OldJournalPageFile(self.html_file("bjmbr_iedboard"))
        self.assertEqual(jspf.anchor_title, "<h1>Editorial Board</h1>")
        self.assertTrue("<h1>Editorial Board</h1>" in jspf.body)

    def test_title_bjmbr_iinstr(self):
        jspf = OldJournalPageFile(self.html_file("bjmbr_iinstruc"))
        self.assertEqual(jspf.anchor_title, "<h1>Instructions to authors</h1>")
        self.assertTrue("<h1>Instructions to authors</h1>" in jspf.body)

    def test_insert_bold_to_p_subtitulo_aa_eedboard(self):
        jspf = OldJournalPageFile(self.html_file("aa_eedboard"))

        self.assertEqual(jspf.body_content.count('class="subtitulo"'), 4)
        self.assertTrue(
            '<p class="subtitulo"><a name="001">Editor-Jefe</a></p>'
            in jspf.body_content
        )
        self.assertTrue(
            '<p class="subtitulo"><a name="0011"></a>Editor-Jefe Sustituto</p>'
            in jspf.body_content
        )
        self.assertTrue(
            '<p class="subtitulo">Comisión editorial</p>' in jspf.body_content
        )
        jspf._insert_bold_to_p_subtitulo()
        self.assertEqual(jspf.body_content.count('class="subtitulo"'), 0)
        self.assertTrue("<p><b>Comisión editorial</b></p>" in jspf.body_content)
        self.assertTrue(
            '<p><b><a name="001">Editor-Jefe</a></b></p>' in jspf.body_content
        )
        self.assertTrue(
            '<p><a name="0011"></a><b>Editor-Jefe Sustituto</b></p>'
            in jspf.body_content
        )

    def test_remove_anchors_abb_pinstruc(self):
        jspf = OldJournalPageFile(self.html_file("abb_pinstruc"))
        self.assertTrue('<a name="end"></a>' in jspf.body_content)
        jspf._remove_anchors()
        self.assertTrue('<a name="end"></a>' not in jspf.body_content)

    def test_remove_anchors_aa_eedboard(self):
        jspf = OldJournalPageFile(self.html_file("aa_eedboard"))

        self.assertEqual(jspf.body_content.count('class="subtitulo"'), 4)
        self.assertTrue(
            '<p class="subtitulo"><a name="001">Editor-Jefe</a></p>'
            in jspf.body_content
        )
        self.assertTrue(
            '<p class="subtitulo"><a name="0011"></a>Editor-Jefe Sustituto</p>'
            in jspf.body_content
        )

        self.assertTrue('<a name="0011"' in jspf.body_content)
        jspf._remove_anchors()
        self.assertTrue(
            '<p class="subtitulo">Editor-Jefe Sustituto</p>' in jspf.body_content
        )

    def test_middle_text_ea_pinstruc(self):
        jspf = OldJournalPageFile(self.html_file("ea_pinstruc"))
        text = "<p>6. As Referências bibliográficas deverão ser citadas"
        self.assertTrue(text in jspf.middle_text)

    def test_read_iso_8859_1_eagri_pedboard(self):
        jspf = OldJournalPageFile(self.html_file("eagri_pedboard"))
        self.assertTrue("Agrícola" in jspf.body_content)
        self.assertTrue("Associação" in jspf.body_content)

    def test_insert_middle_begin_abb_pinstruc(self):
        jspf = OldJournalPageFile(self.html_file("abb_pinstruc"))
        self.assertTrue("Editable" in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf.insert_p_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_insert_middle_begin_aa_eedboard(self):
        jspf = OldJournalPageFile(self.html_file("aa_eedboard"))
        self.assertTrue('href="#0' in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf.insert_p_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_insert_middle_begin_ea_iinstruc(self):
        jspf = OldJournalPageFile(self.html_file("ea_iinstruc"))
        self.assertTrue("script=sci_serial" in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf.insert_p_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_insert_middle_begin_eins_eedboard(self):
        jspf = OldJournalPageFile(self.html_file("eins_eedboard"))
        self.assertTrue("/scielo.php?lng=" in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf.insert_p_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_middle_end_abb_pinstruc(self):
        jspf = OldJournalPageFile(self.html_file("abb_pinstruc"))
        self.assertTrue("javascript:history.back()" in jspf.body_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf.insert_p_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is not None)

    def test_insert_middle_end_aa_eedboard(self):
        jspf = OldJournalPageFile(self.html_file("aa_eedboard"))
        self.assertTrue("script=sci_serial" in jspf.body_content)
        self.assertTrue("Home" in jspf.body_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf.insert_p_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is not None)

    def test_insert_middle_end_bjmbr_iedboard(self):
        jspf = OldJournalPageFile(self.html_file("bjmbr_iedboard"))
        self.assertTrue("script=sci_serial" in jspf.body_content)
        self.assertTrue("Home" in jspf.body_content)

        self.assertNotIn('"middle_end"', jspf.file_content)
        jspf.insert_p_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is not None)

    def test_insert_middle_end_bjgeo_pinstruct(self):
        jspf = OldJournalPageFile(self.html_file("bjgeo_pinstruct"))
        self.assertTrue("script=sci_serial" in jspf.body_content)
        self.assertTrue("Voltar" in jspf.body_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf.insert_p_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is not None)

    def test_insert_middle_end_bjgeo_einstruct(self):
        jspf = OldJournalPageFile(self.html_file("bjgeo_einstruct"))
        self.assertTrue("script=sci_serial" in jspf.body_content)
        self.assertTrue("Volver" in jspf.body_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf.insert_p_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is not None)

    @unittest.skip(
        "Teste não tem comportamento consistente entre o travis e o ambiente de desenvolvimento."
    )
    def test_insert_middle_end_bjmbr_iinstruct(self):
        jspf = OldJournalPageFile(self.html_file("bjmbr_iinstruc"))
        self.assertEqual(jspf.file_content.count("script=sci_serial"), 3)
        self.assertTrue("Home" in jspf.file_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf.insert_p_middle_end()
        self.assertFalse('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is None)
        middle = jspf.middle.strip()
        begin = '<!-- #BeginEditable "texto" -->'
        end = "<p>&nbsp;</p>"
        self.assertEqual(middle[-len(end) :], end)
        self.assertEqual(middle[: len(begin)], begin)

    def test_insert_middle_end_bjmbr_iaboutj(self):
        jspf = OldJournalPageFile(self.html_file("bjmbr_iaboutj"))
        self.assertEqual(len(jspf._body_tree.find_all("li")), 17)
        self.assertEqual(len(jspf._body_tree.find_all("p")), 38)
        self.assertIn(
            "<P>Sociedade Brasileira de Biologia Celular (SBBC) </p>", jspf.file_content
        )
        self.assertEqual(jspf.body.count("<li>"), 13)
        self.assertEqual(jspf.body.count("<p>"), 10)
        self.assertNotIn(
            "<P>Sociedade Brasileira de Biologia Celular (SBBC) </p>", jspf.body_content
        )

    def test_unavailable_msg_es_abb_einstruc(self):
        jspf = OldJournalPageFile(self.html_file("abb_einstruc"))
        self.assertTrue(jspf.ES_UNAVAILABLE_MSG in jspf.unavailable_message)

    def test_unavailable_message_pt_abb_pinstruc(self):
        jspf = OldJournalPageFile(self.html_file("abb_pinstruc"))
        self.assertTrue(jspf.PT_UNAVAILABLE_MSG in jspf.unavailable_message)

    def _in_antes_e_depois(self, file_content, body, antes, depois):
        self.assertIn(antes, file_content)
        self.assertNotIn(depois, file_content)
        self.assertNotIn(antes, body)
        self.assertIn(depois, body)

    def _count_antes_e_depois(self, file_content, body, text, antes=0, depois=0):
        self.assertEqual(file_content.count(text), antes)
        self.assertEqual(body.count(text), depois)

    def test_legacy_info_page_iaboutj(self):
        """
        Teste da ``view function`` ``router_legacy_info_pages``, deve retorna status_code 301 para a página iaboutj
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal(
                {"title": "Revista X", "acronym": "acron_ia"}
            )

            response = self.client.get("/revistas/%s/iaboutj.htm" % journal.url_segment)

            self.assertTrue(301, response.status_code)

    def test_legacy_info_page_edboard(self):
        """
        Teste da ``view function`` ``router_legacy_info_pages``, deve retorna status_code 301 para a página edboard
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal(
                {"title": "Revista X", "acronym": "acron_ed"}
            )

            response = self.client.get("/revistas/%s/edboard.htm" % journal.url_segment)

            self.assertTrue(301, response.status_code)

    def test_legacy_info_page_iinstruc(self):
        """
        Teste da ``view function`` ``router_legacy_info_pages``, deve retorna status_code 301 para a página iinstruc
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal(
                {"title": "Revista X", "acronym": "acron_ii"}
            )

            response = self.client.get(
                "/revistas/%s/iinstruc.htm" % journal.url_segment
            )

            self.assertTrue(301, response.status_code)

    def test_legacy_info_page_isubscrp(self):
        """
        Teste da ``view function`` ``router_legacy_info_pages``, deve retorna status_code 301 para a página isubscrp
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal(
                {"title": "Revista X", "acronym": "acron_isu"}
            )

            response = self.client.get(
                "/revistas/%s/isubscrp.htm" % journal.url_segment
            )

            self.assertTrue(301, response.status_code)
