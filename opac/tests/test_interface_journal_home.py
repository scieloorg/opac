# coding: utf-8

import flask
from flask import url_for, current_app

from base import BaseTestCase

import utils


class JournalHomeTestCase(BaseTestCase):

    # Mission
    def test_journal_detail_mission_with_PT_language(self):
        """
        Teste para verificar se na interface inicial da revista esta retornando
        o texto no idioma Português.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            header = {'Referer': url_for('main.journal_detail',
                                         journal_id=journal.jid)}

            response = c.get(url_for('main.set_locale',
                                     lang_code='pt_BR'),
                             headers=header,
                             follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'pt_BR')

            self.assertIn(u"Esse periódico tem com objetivo xpto",
                          response.data.decode('utf-8'))

    def test_journal_detail_mission_with_ES_language(self):
        """
        Teste para verificar se na interface inicial da revista esta retornando o texto no
        idioma Espanhol.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            header = {'Referer': url_for('main.journal_detail',
                                         journal_id=journal.jid)}

            response = c.get(url_for('main.set_locale',
                                     lang_code='es'),
                             headers=header,
                             follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'es')

            self.assertIn(u"Esta revista tiene como objetivo xpto",
                          response.data.decode('utf-8'))

    def test_journal_detail_mission_with_EN_language(self):
        """
        Teste para verificar se na interface inicial da revista esta retornando
        o texto no idioma Inglês.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            header = {'Referer': url_for('main.journal_detail',
                                         journal_id=journal.jid)}

            response = c.get(url_for('main.set_locale',
                                     lang_code='en'),
                             headers=header,
                             follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'en')

            self.assertIn(u"This journal is aiming xpto",
                          response.data.decode('utf-8'))
