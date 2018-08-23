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
    }

    def test_abb_pinstruc(self):
        jspf = JournalStaticPageFile(self.html['abb_pinstruc'])

        self.assertFalse('"middle_begin"' in str(jspf.tree.body))
        jspf._indicate_middle_begin()
        self.assertTrue('"middle_begin"' in str(jspf.tree.body))
        self.assertTrue('"middle_begin"' in str(jspf._body_tree))
        self.assertTrue(len(jspf._get_middle_children(True, True)) > 0)

"""

    def test_aa_eedboard(self):
        jspf = JournalStaticPageFile(self.html['aa_eedboard'])

        self.assertTrue(jspf.content.strip().endswith('</html>'))
        self.assertTrue(str(jspf.tree.body).endswith('</body>'))
        self.assertEqual(jspf.tree.body, jspf.tree.find('body'))
        self.assertTrue('Home' in str(jspf.tree.body))

        self.assertFalse('"middle_end"' in str(jspf.tree.body))
        jspf._indicate_middle_end()
        self.assertTrue('"middle_end"' in str(jspf.tree.body))

        self.assertFalse('"middle_begin"' in str(jspf.tree.body))
        jspf._indicate_middle_begin()
        self.assertTrue('"middle_begin"' in str(jspf.tree.body))

        self.assertFalse('Home' in str(jspf.middle_text))

    def test_ea_iinstruc(self):
        jspf = JournalStaticPageFile(self.html['ea_iinstruc'])
        self.assertFalse('"middle_begin"' in str(jspf.tree.body))
        jspf._indicate_middle_begin()
        self.assertTrue('"middle_begin"' in str(jspf.tree.body))

    def test_ea_pinstruc(self):
        jspf = JournalStaticPageFile(self.html['ea_pinstruc'])
        text = '<p>6. As Referências bibliográficas deverão ser citadas no  texto,'
        self.assertTrue(text in jspf.middle_text)

        #self.assertEqual(jspf.sorted_by_relevance, [])
        #self.assertEqual(jspf.PT_UNAVAILABLE_MSG, jspf.unavailable_message)

    def test_abb_einstruc(self):
        jspf = JournalStaticPageFile(self.html['abb_einstruc'])
        #self.assertEqual(jspf.ES_UNAVAILABLE_MSG, jspf.unavailable_message)
"""
