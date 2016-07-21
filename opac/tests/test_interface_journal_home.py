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

    def test_journal_without_social_networks_show_no_links(self):
        """
        COM:
            - Periódico sem redes socials
        QUANDO:
            - Acessarmos a home do periódico
        VERIFICAMOS:
            - Que não aparece a seção de redes sociais
            - O div com class="journalLinks" deve aparecer
        """

        with current_app.app_context():
            # with
            collection = utils.makeOneCollection()
            journal = utils.makeOneJournal({'collection': collection})
            with self.client as c:
                # when
                response = c.get(url_for('main.journal_detail', journal_id=journal.jid))
                # then
                self.assertEqual(journal.social_networks, [])
                self.assertStatus(response, 200)
                social_networks_class = u"journalLinks"
                self.assertIn(social_networks_class, response.data.decode('utf-8'))
                twitter_btn_class = u"bigTwitter"
                self.assertNotIn(twitter_btn_class, response.data.decode('utf-8'))
                facebook_btn_class = u"bigFacebook"
                self.assertNotIn(facebook_btn_class, response.data.decode('utf-8'))
                google_btn_class = u"bigGooglePlus"
                self.assertNotIn(google_btn_class, response.data.decode('utf-8'))

    def test_journal_with_twitter_social_networks_show_links(self):
        """
        COM:
            - Periódico COM redes socials
        QUANDO:
            - Acessarmos a home do periódico
        VERIFICAMOS:
            - Que SIM aparece a seção de redes sociais
            - O div com class="journalLinks" deve aparecer
        """

        with current_app.app_context():
            # with
            collection = utils.makeOneCollection()
            journal_data = {
                'collection': collection,
                'social_networks': [
                    {
                        'network': u'twitter',
                        'account': u'http://twitter.com/@foo'
                    }
                ]
            }
            journal = utils.makeOneJournal(journal_data)
            with self.client as c:
                # when
                response = c.get(url_for('main.journal_detail', journal_id=journal.jid))
                # then
                self.assertStatus(response, 200)
                social_networks_class = u"journalLinks"
                self.assertIn(social_networks_class, response.data.decode('utf-8'))
                twitter_btn_class = u"bigTwitter"
                self.assertIn(twitter_btn_class, response.data.decode('utf-8'))
                facebook_btn_class = u"bigFacebook"
                self.assertNotIn(facebook_btn_class, response.data.decode('utf-8'))
                google_btn_class = u"bigGooglePlus"
                self.assertNotIn(google_btn_class, response.data.decode('utf-8'))

                expected_social_link = u'<a href="{account}" data-toggle="tooltip" title="{network}">'.format(
                    account=journal_data['social_networks'][0]['account'],
                    network=journal_data['social_networks'][0]['network'].title(),
                )
                self.assertIn(expected_social_link, response.data.decode('utf-8'))

    def test_journal_with_facebook_social_networks_show_links(self):
        """
        COM:
            - Periódico COM redes socials
        QUANDO:
            - Acessarmos a home do periódico
        VERIFICAMOS:
            - Que SIM aparece a seção de redes sociais
            - O div com class="journalLinks" deve aparecer
        """

        with current_app.app_context():
            # with
            collection = utils.makeOneCollection()
            journal_data = {
                'collection': collection,
                'social_networks': [
                    {
                        'network': u'facebook',
                        'account': u'http://facebook.com/foo'
                    }
                ]
            }
            journal = utils.makeOneJournal(journal_data)
            with self.client as c:
                # when
                response = c.get(url_for('main.journal_detail', journal_id=journal.jid))
                # then
                self.assertStatus(response, 200)
                social_networks_class = u"journalLinks"
                self.assertIn(social_networks_class, response.data.decode('utf-8'))
                twitter_btn_class = u"bigTwitter"
                self.assertNotIn(twitter_btn_class, response.data.decode('utf-8'))
                facebook_btn_class = u"bigFacebook"
                self.assertIn(facebook_btn_class, response.data.decode('utf-8'))
                google_btn_class = u"bigGooglePlus"
                self.assertNotIn(google_btn_class, response.data.decode('utf-8'))

                expected_social_link = u'<a href="{account}" data-toggle="tooltip" title="{network}">'.format(
                    account=journal_data['social_networks'][0]['account'],
                    network=journal_data['social_networks'][0]['network'].title(),
                )
                self.assertIn(expected_social_link, response.data.decode('utf-8'))

    def test_journal_with_googleplus_social_networks_show_links(self):
        """
        COM:
            - Periódico COM redes socials
        QUANDO:
            - Acessarmos a home do periódico
        VERIFICAMOS:
            - Que SIM aparece a seção de redes sociais
            - O div com class="journalLinks" deve aparecer
        """

        with current_app.app_context():
            # with
            collection = utils.makeOneCollection()
            journal_data = {
                'collection': collection,
                'social_networks': [
                    {
                        'network': u'google',
                        'account': u'http://plus.google.com/+foo'
                    }
                ]
            }
            journal = utils.makeOneJournal(journal_data)
            with self.client as c:
                # when
                response = c.get(url_for('main.journal_detail', journal_id=journal.jid))
                # then
                self.assertStatus(response, 200)
                social_networks_class = u"journalLinks"
                self.assertIn(social_networks_class, response.data.decode('utf-8'))
                twitter_btn_class = u"bigTwitter"
                self.assertNotIn(twitter_btn_class, response.data.decode('utf-8'))
                facebook_btn_class = u"bigFacebook"
                self.assertNotIn(facebook_btn_class, response.data.decode('utf-8'))
                google_btn_class = u"bigGooglePlus"
                self.assertIn(google_btn_class, response.data.decode('utf-8'))

                expected_social_link = u'<a href="{account}" data-toggle="tooltip" title="{network}">'.format(
                    account=journal_data['social_networks'][0]['account'],
                    network=journal_data['social_networks'][0]['network'].title(),
                )
                self.assertIn(expected_social_link, response.data.decode('utf-8'))
