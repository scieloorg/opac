# coding: utf-8

import os
from .base import BaseTestCase

from webapp.utils.journal_static_page import (
    JournalStaticPageFile,
    JournalNewPages,
)


REVISTAS_PATH = 'opac/tests/fixtures/pages/revistas'
IMG_REVISTAS_PATH = 'opac/tests/fixtures/pages/img_revistas'


class UtilsJournalPagesTestCase(BaseTestCase):

    def test_rbep_get_new_journal_page(self):
        expected = [
                    '/img/revistas/rbep/CNPq logo.gif',
                    '/img/revistas/rbep/Logotipo Financiador 1 - FACED.jpg',
                    '/img/revistas/rbep/Logotipo Financiador 2 - PROPESQ.jpg',
                    '/img/revistas/rbep/Logotipo Financiador 3 -PAEP.jpg',
                    '/img/revistas/rbep/Logotipo Instituição Mantenedora.jpg',
                    ]
        new_pgs = JournalNewPages(
            'www.scielo.br', REVISTAS_PATH, IMG_REVISTAS_PATH, 'rbep')
        files = ['paboutj.htm', 'pedboard.htm', 'pinstruc.htm']
        content, images_in_file = new_pgs.get_new_journal_page(files)

        files = ['eaboutj.htm', 'eedboard.htm', 'einstruc.htm']
        content, images_in_file = new_pgs.get_new_journal_page(files)
        self.assertEqual(expected, images_in_file)

    def test_rbep_get_journal_page_img_paths(self):
        images_in_file = [
            '/img/revistas/rbep/CNPq logo.gif',
            '/img/revistas/rbep/Logotipo Financiador 1 - FACED.jpg',
            '/img/revistas/rbep/Logotipo Financiador 2 - PROPESQ.jpg',
            '/img/revistas/rbep/Logotipo Financiador 3 -PAEP.jpg',
            '/img/revistas/rbep/Logotipo Instituição Mantenedora.jpg',
            ]
        expected = [
            ('/img/revistas/rbep/CNPq logo.gif',
             os.path.join(IMG_REVISTAS_PATH, 'rbep/CNPq logo.gif'),
             'rbep_cnpq-logo.gif'),
            ('/img/revistas/rbep/Logotipo Financiador 1 - FACED.jpg',
             os.path.join(
                IMG_REVISTAS_PATH,
                'rbep/Logotipo Financiador 1 - FACED.jpg'),
             'rbep_logotipo-financiador-1-faced.jpg'),
            ('/img/revistas/rbep/Logotipo Financiador 2 - PROPESQ.jpg',
             os.path.join(
                IMG_REVISTAS_PATH,
                'rbep/Logotipo Financiador 2 - PROPESQ.jpg'),
             'rbep_logotipo-financiador-2-propesq.jpg'),
            ('/img/revistas/rbep/Logotipo Financiador 3 -PAEP.jpg',
             os.path.join(
                IMG_REVISTAS_PATH,
                'rbep/Logotipo Financiador 3 -PAEP.jpg'),
             'rbep_logotipo-financiador-3-paep.jpg'),
            ('/img/revistas/rbep/Logotipo Instituição Mantenedora.jpg',
             os.path.join(
                IMG_REVISTAS_PATH,
                'rbep/Logotipo Instituição Mantenedora.jpg'),
             'rbep_logotipo-instituicao-mantenedora.jpg'),
            ]
        expected = sorted(expected)
        new_pgs = JournalNewPages(
            'www.scielo.br', REVISTAS_PATH, IMG_REVISTAS_PATH, 'rbep')
        journal_img_paths = new_pgs.get_journal_page_img_paths(images_in_file)
        self.assertEqual(len(images_in_file), 5)
        self.assertEqual(len(journal_img_paths), 5)
        for expected_item, img_path in zip(expected, journal_img_paths):
            self.assertEqual(expected_item, img_path)

        images_in_file.append('/img/revistas/rbep/CNPq logo.gif')
        journal_img_paths = new_pgs.get_journal_page_img_paths(images_in_file)
        self.assertEqual(len(images_in_file), 6)
        self.assertEqual(len(journal_img_paths), 5)
        for expected_item, img_path in zip(expected, journal_img_paths):
            self.assertEqual(expected_item, img_path)

        images_in_file.append('/img/revistas/rbep/logo.gif')
        expected.append(('/img/revistas/rbep/logo.gif',
                         os.path.join(IMG_REVISTAS_PATH, 'rbep/logo.gif'),
                         'rbep_logo.gif'
                         ))
        journal_img_paths = new_pgs.get_journal_page_img_paths(images_in_file)
        self.assertEqual(len(images_in_file), 7)
        self.assertEqual(len(journal_img_paths), 6)
        for expected_item, img_path in zip(expected, journal_img_paths):
            self.assertEqual(expected_item, img_path)

        images_in_file.append('/img/revistas/rbep/nao_existe.gif')
        journal_img_paths = new_pgs.get_journal_page_img_paths(images_in_file)
        self.assertEqual(len(images_in_file), 8)
        self.assertEqual(len(journal_img_paths), 6)
        for expected_item, img_path in zip(expected, journal_img_paths):
            self.assertEqual(expected_item, img_path)


class JournalStaticPageTestCase(BaseTestCase):

    def html_file(self, name):
        f = os.path.join(REVISTAS_PATH, name.replace('_', '/')+'.htm')
        if os.path.isfile(f):
            return f

    def test_title_icse_eaboutj(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('icse_eaboutj'))
        self.assertEqual(
            jspf.acron, 'icse')
        self.assertEqual(
            jspf.anchor_title, '<h1>Acerca de la revista</h1>')
        self.assertTrue(
            '<h1>Acerca de la revista</h1>' in jspf.body)

    def test_title_eins_eedboar(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('eins_eedboard'))
        self.assertEqual(jspf.anchor_title, '<h1>Cuerpo Editorial</h1>')
        self.assertTrue(
            '<h1>Cuerpo Editorial</h1>' in jspf.body)

    def test_title_abb_einstruc(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('abb_einstruc'))
        self.assertEqual(
            jspf.anchor_title, '<h1>Instrucciones a los autores</h1>')
        self.assertTrue(
            '<h1>Instrucciones a los autores</h1>' in jspf.body)

    def test_title_bjgeo_einstr(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('bjgeo_einstruct'))
        self.assertEqual(
            jspf.anchor_title, '<h1>Instrucciones a los autores</h1>')
        self.assertTrue(
            '<h1>Instrucciones a los autores</h1>' in jspf.body)

    def test_title_bjmbr_pabout(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('bjmbr_paboutj'))
        self.assertEqual(jspf.anchor_title, '<h1>Sobre o periódico</h1>')
        self.assertTrue(
            '<h1>Sobre o periódico</h1>' in jspf.body)

    def test_title_eagri_pedboa(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('eagri_pedboard'))
        self.assertEqual(jspf.anchor_title, '<h1>Corpo Editorial</h1>')
        self.assertTrue(
            '<h1>Corpo Editorial</h1>' in jspf.body)

    def test_title_abb_pinstruc(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('abb_pinstruc'))
        self.assertEqual(jspf.anchor_title, '<h1>Instruções aos autores</h1>')
        self.assertTrue(
            '<h1>Instruções aos autores</h1>' in jspf.body)

    def test_title_bjgeo_pinstr(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('bjgeo_pinstruct'))
        self.assertEqual(jspf.anchor_title, '<h1>Instruções aos autores</h1>')
        self.assertTrue(
            '<h1>Instruções aos autores</h1>' in jspf.body)

    def test_title_bjmbr_iabout(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('bjmbr_iaboutj'))
        self.assertEqual(jspf.anchor_title, '<h1>About the journal</h1>')
        self.assertTrue(
            '<h1>About the journal</h1>' in jspf.body)

    def test_title_bjmbr_iedboa(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('bjmbr_iedboard'))
        self.assertEqual(jspf.anchor_title, '<h1>Editorial Board</h1>')
        self.assertTrue(
            '<h1>Editorial Board</h1>' in jspf.body)

    def test_title_bjmbr_iinstr(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('bjmbr_iinstruc'))
        self.assertEqual(jspf.anchor_title, '<h1>Instructions to authors</h1>')
        self.assertTrue(
            '<h1>Instructions to authors</h1>' in jspf.body)

    def test_insert_bold_to_p_subtitulo_aa_eedboard(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('aa_eedboard'))

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
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('abb_pinstruc'))
        self.assertTrue('<a name="end"></a>' in jspf.body_content)
        jspf._remove_anchors()
        self.assertTrue('<a name="end"></a>' not in jspf.body_content)

    def test_remove_anchors_aa_eedboard(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('aa_eedboard'))

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
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('ea_pinstruc'))
        text = '<p>6. As Referências bibliográficas deverão ser citadas'
        self.assertTrue(text in jspf.middle_text)

    def test_read_iso_8859_1_eagri_pedboard(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('eagri_pedboard'))
        self.assertTrue('Agrícola' in jspf.body_content)
        self.assertTrue('Associação' in jspf.body_content)

    def test_insert_middle_begin_abb_pinstruc(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('abb_pinstruc'))
        self.assertTrue('Editable' in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf.insert_p_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_insert_middle_begin_aa_eedboard(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('aa_eedboard'))
        self.assertTrue('href="#0' in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf.insert_p_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_insert_middle_begin_ea_iinstruc(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('ea_iinstruc'))
        self.assertTrue('script=sci_serial' in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf.insert_p_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_insert_middle_begin_eins_eedboard(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('eins_eedboard'))
        self.assertTrue('/scielo.php?lng=' in jspf.body_content)
        self.assertFalse('"middle_begin"' in jspf.body_content)
        jspf.insert_p_middle_begin()
        self.assertTrue('"middle_begin"' in jspf.body_content)

    def test_middle_end_abb_pinstruc(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('abb_pinstruc'))
        self.assertTrue('javascript:history.back()' in jspf.body_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf.insert_p_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is not None)

    def test_insert_middle_end_aa_eedboard(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('aa_eedboard'))
        self.assertTrue('script=sci_serial' in jspf.body_content)
        self.assertTrue('Home' in jspf.body_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf.insert_p_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is not None)

    def test_insert_middle_end_bjmbr_iedboard(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('bjmbr_iedboard'))
        self.assertTrue('script=sci_serial' in jspf.body_content)
        self.assertTrue('Home' in jspf.body_content)

        self.assertNotIn('"middle_end"', jspf.file_content)
        jspf.insert_p_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is not None)

    def test_insert_middle_end_bjgeo_pinstruct(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('bjgeo_pinstruct'))
        self.assertTrue('script=sci_serial' in jspf.body_content)
        self.assertTrue('Voltar' in jspf.body_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf.insert_p_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is not None)

    def test_insert_middle_end_bjgeo_einstruct(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('bjgeo_einstruct'))
        self.assertTrue('script=sci_serial' in jspf.body_content)
        self.assertTrue('Volver' in jspf.body_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf.insert_p_middle_end()
        self.assertTrue('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is not None)

    def test_insert_middle_end_bjmbr_iinstruct(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('bjmbr_iinstruc'))
        self.assertEqual(jspf.file_content.count('script=sci_serial'), 3)
        self.assertTrue('Home' in jspf.file_content)
        self.assertFalse('"middle_end"' in jspf.body_content)
        jspf.insert_p_middle_end()
        self.assertFalse('"middle_end"' in jspf.body_content)
        self.assertTrue(jspf.p_middle_end is None)
        middle = jspf.middle.strip()
        begin = '<!-- #BeginEditable "texto" -->'
        end = '<p>&nbsp;</p>'
        self.assertEqual(middle[-len(end):], end)
        self.assertEqual(middle[:len(begin)], begin)

    def test_insert_middle_end_bjmbr_iaboutj(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('bjmbr_iaboutj'))
        self.assertEqual(len(jspf._body_tree.find_all('li')), 17)
        self.assertEqual(len(jspf._body_tree.find_all('p')), 27)
        self.assertIn(
            '<P>Sociedade Brasileira de Biologia Celular (SBBC) </p>',
            jspf.file_content)
        self.assertEqual(jspf.body.count('<li>'), 13)
        self.assertEqual(jspf.body.count('<p>'), 10)
        self.assertNotIn(
            '<P>Sociedade Brasileira de Biologia Celular (SBBC) </p>',
            jspf.body_content)

    def test_unavailable_msg_es_abb_einstruc(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('abb_einstruc'))
        self.assertTrue(jspf.ES_UNAVAILABLE_MSG in jspf.unavailable_message)

    def test_unavailable_message_pt_abb_pinstruc(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('abb_pinstruc'))
        self.assertTrue(jspf.PT_UNAVAILABLE_MSG in jspf.unavailable_message)

    def _in_antes_e_depois(self, file_content, body, antes, depois):
        self.assertIn(antes, file_content)
        self.assertNotIn(depois, file_content)
        self.assertNotIn(antes, body)
        self.assertIn(depois, body)

    def _count_antes_e_depois(self, file_content, body, text, antes=0, depois=0):
        self.assertEqual(file_content.count(text), antes)
        self.assertEqual(body.count(text), depois)

    def test_title_icse_iinstruc_remove_original_website_location(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('icse_iinstruc'))

        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            'indexSearch=AU&exprSearch=', antes=12)
        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            '//search.scielo.org/?q=au:', depois=12)

        self._in_antes_e_depois(
            jspf.file_content, jspf.body,
            'http://www.scielo.br/cgi-bin/wxis.exe/iah/'
            '?IsisScript=iah/iah.xis&base=article%5Edlibrary&format=iso.pft&'
            'lang=p&nextAction=lnk&'
            'indexSearch=AU&exprSearch=MEIERHOFFER,+LILIAN+KOZSLOWSKI',
            '//search.scielo.org/?q=au:MEIERHOFFER,+LILIAN+KOZSLOWSKI')

        self.assertIn('/img/revistas/icse/levels.pdf', jspf.body)

        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            'www.scielo.br/img/revistas/icse/levels.pdf',
            antes=2, depois=1)

        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            'www.scielo.br/revistas/icse/levels.pdf',
            antes=2, depois=1)
        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            '"/revistas/icse/levels.pdf"',
            depois=1)

        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            'www.scielo.br/revistas/icse/iinstruc.htm',
            antes=2)
        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            '"/journal/icse/about/#instructions"',
            depois=1)
        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            '/journal/icse/about/#instructions',
            depois=2)
        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            'www.scielo.br/journal/icse/about/#instructions',
            depois=1)

        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            'www.scielo.br/revistas/icse/iaboutj.htm',
            antes=2)
        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            '"/journal/icse/about/#about"',
            depois=1)
        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            '/journal/icse/about/#about',
            depois=2)
        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            'www.scielo.br/journal/icse/about/#about',
            depois=1)

        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            'www.scielo.br/revistas/icse/iedboard.htm',
            antes=2)
        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            '"/journal/icse/about/#editors"',
            depois=1)
        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            '/journal/icse/about/#editors',
            depois=2)
        self._count_antes_e_depois(
            jspf.file_content, jspf.body,
            'www.scielo.br/journal/icse/about/#editors',
            depois=1)

        self.assertIn(
            '<p><a href="http://www.scielo.br/revistas/'
            'icse/www1.folha.uol.com.br">www1.folha.uol.com.br</a></p>',
            jspf.file_content)
        self.assertIn(
            '<p><a href="http://www1.folha.uol.com.br">'
            'www1.folha.uol.com.br</a></p>',
            jspf.body)

        self.assertIn('http://www.scielo.br/clinics', jspf.file_content)
        self.assertIn('http://www.scielo.br/clinics', jspf.body)

        self.assertEqual(
            jspf.file_content.count(
                'http://www.scielo.br/scielo.php?script=sci_serial&'
                'pid=0102-4450&lng=en&nrm=iso'),
            1)
        self.assertEqual(
            jspf.body.count(
                'http://www.scielo.br/scielo.php?script=sci_serial&amp;'
                'pid=0102-4450&amp;lng=en&amp;nrm=iso'),
            0)
        self.assertEqual(
            jspf.body.count(
                '/scielo.php?script=sci_serial&amp;'
                'pid=0102-4450&amp;lng=en&amp;nrm=iso'),
            2)

    def test_title_icse_eaboutj_remove_original_website_location(self):
        jspf = JournalStaticPageFile(
            'www.scielo.br', self.html_file('icse_eaboutj'))
        url = 'www.scielo.br/icse'
        self.assertEqual(jspf.file_content.count(url), 2)
        self.assertEqual(jspf.body.count(url), 0)
        self.assertEqual(jspf.body.count('/journal/icse/'), 2)
        self.assertIn('/journal/icse/', jspf.body)
