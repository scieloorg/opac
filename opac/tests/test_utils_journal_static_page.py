# coding: utf-8

import os
from .base import BaseTestCase

from . import utils

from webapp.utils.journal_static_page import JournalStaticPageFile


"""
abb/eedboard.htm (unavailable)
ea/eaboutj.htm (header contains 'href="#0')
abb/iaboutj.htm
    (header contains 'Editable')
    <p class="subtitulo"><b><a name="03"></a>Intellectual Property</b></p>
    <p class="subtitulo"><a name="04"><b>Sponsor</b></a></p>
    footer padrao
abb/iinstruc.htm
    <p class="subtitulo"><em><a name="001"><b>Scope of the journal</b></a></em></p>
    codificacao
ea/eedboard.htm
<p class="subtitulo"><a name="001"></a><b>Editor</b></p>
"""

FIXTURE_PATH = 'opac/tests/pages/'


class JournalStaticPageTestCase(BaseTestCase):

    html = {
        'aa_eedboard': FIXTURE_PATH+'aa/eedboard.htm',
        'ea_iinstruc': FIXTURE_PATH+'ea/iinstruc.htm',
        'ea_pinstruc': FIXTURE_PATH+'ea/pinstruc.htm',
        'abb_pinstruc': FIXTURE_PATH+'abb/pinstruc.htm',
        'abb_einstruc': FIXTURE_PATH+'abb/einstruc.htm',
        'eagri_pedboard': FIXTURE_PATH+'eagri/pedboard.htm',
        'eins_eedboard': FIXTURE_PATH+'eins/eedboard.htm',
    }

    def test_insert_bold_to_p_subtitulo_aa_eedboard(self):
        jspf = JournalStaticPageFile(self.html['aa_eedboard'])

        self.assertEqual(jspf.body_content.count('class="subtitulo"'), 4)
        self.assertTrue(
            '<p class="subtitulo"><a name="001">Editor-Jefe</a></p>'
            in jspf.body_content
        )
        self.assertTrue(
            '<p class="subtitulo"><a name="0011"></a>Editor-Jefe Sustituto</p>'
            in jspf.body_content)
        self.assertTrue(
            '<p class="subtitulo">Comisión editorial</p>' in
            jspf.body_content)
        jspf._insert_bold_to_p_subtitulo()
        self.assertEqual(jspf.body_content.count('class="subtitulo"'), 0)
        self.assertTrue(
            '<p><b>Comisión editorial</b></p>' in jspf.body_content)
        self.assertTrue(
            '<p><b><a name="001">Editor-Jefe</a></b></p>' in jspf.body_content
        )
        self.assertTrue(
            '<p><a name="0011"></a><b>Editor-Jefe Sustituto</b></p>'
            in jspf.body_content)

    def test_remove_anchors_abb_pinstruc(self):
        jspf = JournalStaticPageFile(self.html['abb_pinstruc'])
        self.assertTrue('<a name="end"></a>' in jspf.body_content)
        jspf._remove_anchors()
        self.assertTrue('<a name="end"></a>' not in jspf.body_content)

    def test_remove_anchors_aa_eedboard(self):
        jspf = JournalStaticPageFile(self.html['aa_eedboard'])

        self.assertEqual(jspf.body_content.count('class="subtitulo"'), 4)
        self.assertTrue(
            '<p class="subtitulo"><a name="001">Editor-Jefe</a></p>'
            in jspf.body_content
        )
        self.assertTrue(
            '<p class="subtitulo"><a name="0011"></a>Editor-Jefe Sustituto</p>'
            in jspf.body_content)

        self.assertTrue('<a name="0011"' in jspf.body_content)
        jspf._remove_anchors()
        self.assertTrue(
            '<p class="subtitulo">Editor-Jefe Sustituto</p>'
            in jspf.body_content)

    def test_middle_text_ea_pinstruc(self):
        jspf = JournalStaticPageFile(self.html['ea_pinstruc'])
        text = '<p>6. As Referências bibliográficas deverão ser citadas no  texto,'
        self.assertTrue(text in jspf.middle_text)

    def test_read_iso_8859_1_eagri_pedboard(self):
        jspf = JournalStaticPageFile(self.html['eagri_pedboard'])
        self.assertTrue('Agrícola' in jspf.body_content)
        self.assertTrue('Associação' in jspf.body_content)

    def test_indicate_middle_begin_abb_pinstruc(self):
        jspf = JournalStaticPageFile(self.html['abb_pinstruc'])
        self.assertTrue('Editable' in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf._indicate_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_indicate_middle_begin_aa_eedboard(self):
        jspf = JournalStaticPageFile(self.html['aa_eedboard'])
        self.assertTrue('href="#0' in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf._indicate_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_indicate_middle_begin_ea_iinstruc(self):
        jspf = JournalStaticPageFile(self.html['ea_iinstruc'])
        self.assertTrue('script=sci_serial' in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf._indicate_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_indicate_middle_begin_eins_eedboard(self):
        jspf = JournalStaticPageFile(self.html['eins_eedboard'])
        self.assertTrue('/scielo.php?lng=' in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf._indicate_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_middle_end_abb_pinstruc(self):
        jspf = JournalStaticPageFile(self.html['abb_pinstruc'])
        self.assertTrue('javascript:history.back()' in jspf.body_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf._indicate_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)

    def test_indicate_middle_end_aa_eedboard(self):
        jspf = JournalStaticPageFile(self.html['aa_eedboard'])
        self.assertTrue('script=sci_serial' in jspf.body_content)
        self.assertTrue('Home' in jspf.body_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf._indicate_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)

    def test_unavailable_msg_es_abb_einstruc(self):
        jspf = JournalStaticPageFile(self.html['abb_einstruc'])
        self.assertTrue(jspf.ES_UNAVAILABLE_MSG in jspf.unavailable_message)

    def test_unavailable_message_pt_abb_pinstruc(self):
        jspf = JournalStaticPageFile(self.html['abb_pinstruc'])
        self.assertTrue(jspf.PT_UNAVAILABLE_MSG in jspf.unavailable_message)
