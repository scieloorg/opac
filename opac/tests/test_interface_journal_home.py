# coding: utf-8

import os
import flask
from flask import url_for, current_app

from .base import BaseTestCase

from . import utils


class JournalHomeTestCase(BaseTestCase):

    # Mission
    def test_journal_detail_mission_with_pt_language(self):
        """
        Teste para verificar se na interface inicial da revista esta retornando
        o texto no idioma Português.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            header = {'Referer': url_for('main.journal_detail',
                                         url_seg=journal.url_segment)}

            response = c.get(url_for('main.set_locale',
                                     lang_code='pt_BR'),
                             headers=header,
                             follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'pt_BR')

            self.assertIn("Esse periódico tem com objetivo xpto",
                          response.data.decode('utf-8'))

    def test_journal_detail_mission_with_es_language(self):
        """
        Teste para verificar se na interface inicial da revista esta retornando o texto no
        idioma Espanhol.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            header = {'Referer': url_for('main.journal_detail',
                                         url_seg=journal.url_segment)}

            response = c.get(url_for('main.set_locale',
                                     lang_code='es'),
                             headers=header,
                             follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'es')

            self.assertIn("Esta revista tiene como objetivo xpto",
                          response.data.decode('utf-8'))

    def test_journal_detail_mission_with_en_language(self):
        """
        Teste para verificar se na interface inicial da revista esta retornando
        o texto no idioma Inglês.
        """
        journal = utils.makeOneJournal()

        with self.client as c:
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            header = {'Referer': url_for('main.journal_detail',
                                         url_seg=journal.url_segment)}

            response = c.get(
                url_for('main.set_locale', lang_code='en'),
                headers=header,
                follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(flask.session['lang'], 'en')

            self.assertIn("This journal is aiming xpto",
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
                response = c.get(url_for('main.journal_detail', url_seg=journal.url_segment))
                # then
                self.assertEqual(journal.social_networks, [])
                self.assertStatus(response, 200)
                social_networks_class = "journalLinks"
                self.assertIn(social_networks_class, response.data.decode('utf-8'))
                twitter_btn_class = "bigTwitter"
                self.assertNotIn(twitter_btn_class, response.data.decode('utf-8'))
                facebook_btn_class = "bigFacebook"
                self.assertNotIn(facebook_btn_class, response.data.decode('utf-8'))
                google_btn_class = "bigGooglePlus"
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
                        'network': 'twitter',
                        'account': 'http://twitter.com/@foo'
                    }
                ]
            }
            journal = utils.makeOneJournal(journal_data)
            with self.client as c:
                # when
                response = c.get(url_for('main.journal_detail', url_seg=journal.url_segment))
                # then
                self.assertStatus(response, 200)
                social_networks_class = "journalLinks"
                self.assertIn(social_networks_class, response.data.decode('utf-8'))
                twitter_btn_class = "bigTwitter"
                self.assertIn(twitter_btn_class, response.data.decode('utf-8'))
                facebook_btn_class = "bigFacebook"
                self.assertNotIn(facebook_btn_class, response.data.decode('utf-8'))
                google_btn_class = "bigGooglePlus"
                self.assertNotIn(google_btn_class, response.data.decode('utf-8'))

                expected_social_link = '<a href="{account}" data-toggle="tooltip" title="{network}">'.format(
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
                        'network': 'facebook',
                        'account': 'http://facebook.com/foo'
                    }
                ]
            }
            journal = utils.makeOneJournal(journal_data)
            with self.client as c:
                # when
                response = c.get(url_for('main.journal_detail', url_seg=journal.url_segment))
                # then
                self.assertStatus(response, 200)
                social_networks_class = "journalLinks"
                self.assertIn(social_networks_class, response.data.decode('utf-8'))
                twitter_btn_class = "bigTwitter"
                self.assertNotIn(twitter_btn_class, response.data.decode('utf-8'))
                facebook_btn_class = "bigFacebook"
                self.assertIn(facebook_btn_class, response.data.decode('utf-8'))
                google_btn_class = "bigGooglePlus"
                self.assertNotIn(google_btn_class, response.data.decode('utf-8'))

                expected_social_link = '<a href="{account}" data-toggle="tooltip" title="{network}">'.format(
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
                        'network': 'google',
                        'account': 'http://plus.google.com/+foo'
                    }
                ]
            }
            journal = utils.makeOneJournal(journal_data)
            with self.client as c:
                # when
                response = c.get(url_for('main.journal_detail', url_seg=journal.url_segment))
                # then
                self.assertStatus(response, 200)
                social_networks_class = "journalLinks"
                self.assertIn(social_networks_class, response.data.decode('utf-8'))
                twitter_btn_class = "bigTwitter"
                self.assertNotIn(twitter_btn_class, response.data.decode('utf-8'))
                facebook_btn_class = "bigFacebook"
                self.assertNotIn(facebook_btn_class, response.data.decode('utf-8'))
                google_btn_class = "bigGooglePlus"
                self.assertIn(google_btn_class, response.data.decode('utf-8'))

                expected_social_link = '<a href="{account}" data-toggle="tooltip" title="{network}">'.format(
                    account=journal_data['social_networks'][0]['account'],
                    network=journal_data['social_networks'][0]['network'].title(),
                )
                self.assertIn(expected_social_link, response.data.decode('utf-8'))

    def test_journal_scimago_link(self):
        """
        COM:
            - Periódico COM scimago_id
        QUANDO:
            - Acessarmos a home do periódico
        VERIFICAMOS:
            - Que SIM aparece o link para scimago
        """
        with current_app.app_context():
            # with
            collection = utils.makeOneCollection()
            journal_data = {
                'collection': collection,
                'scimago_id': '22596',
            }
            journal = utils.makeOneJournal(journal_data)
            with self.client as c:
                # when
                response = c.get(
                    url_for('main.journal_detail',
                            url_seg=journal.url_segment))
                response_data = response.data.decode('utf-8')
                # then
                expected = 'https://www.scimagojr.com/journalsearch.php?tip=sid&clean=0&q=22596'
                if '&amp;' in response_data:
                    expected = expected.replace('&', '&amp;')
                self.assertStatus(response, 200)
                self.assertIn(expected, response_data)

                expected = '<a target="_blank" href="{}">Scimago'.format(expected)
                self.assertIn(expected, response_data)

    def test_journal_scimago_enabled_is_false(self):
        """
        COM:
            - Periódico COM scimago_id
            - SCIMAGO_ENABLED is False
        QUANDO:
            - Acessarmos a home do periódico
        VERIFICAMOS:
            - Que NÃO aparece o link para scimago
        """
        with current_app.app_context():
            # with
            SCIMAGO_ENABLED = current_app.config['SCIMAGO_ENABLED']
            current_app.config['SCIMAGO_ENABLED'] = False
            collection = utils.makeOneCollection()
            journal_data = {
                'collection': collection,
                'scimago_id': '22596',
            }
            journal = utils.makeOneJournal(journal_data)
            with self.client as c:
                # when
                response = c.get(
                    url_for('main.journal_detail',
                            url_seg=journal.url_segment))
                response_data = response.data.decode('utf-8')
                # then
                self.assertStatus(response, 200)
                expected = 'https://www.scimagojr.com/journalsearch.php?tip=sid&clean=0&q=22596'
                self.assertNotIn(expected, response_data)

                expected = '<a target="_blank" href="{}">Scimago'.format(expected)
                self.assertNotIn(expected, response_data)
            current_app.config['SCIMAGO_ENABLED'] = SCIMAGO_ENABLED

    def test_journal_scimago_is_none(self):
        """
        COM:
            - Periódico SEM scimago_id
        QUANDO:
            - Acessarmos a home do periódico
        VERIFICAMOS:
            - Que NÃO aparece o link para scimago
        """
        with current_app.app_context():
            # with
            collection = utils.makeOneCollection()
            journal_data = {
                'collection': collection,
            }
            journal = utils.makeOneJournal(journal_data)
            with self.client as c:
                # when
                response = c.get(
                    url_for('main.journal_detail',
                            url_seg=journal.url_segment))
                response_data = response.data.decode('utf-8')
                
                expected = 'https://www.scimagojr.com/journalsearch.php?tip=sid&clean=0&q='
                if '&amp;' in response_data:
                    expected = expected.replace('&', '&amp;')
                # then
                self.assertStatus(response, 200)
                self.assertNotIn(expected, response_data)

                expected = '<a target="_blank" href="{}">Scimago'.format(expected)
                self.assertNotIn(expected, response_data)

    def test_journal_scimago_url_config(self):
        """
        COM:
            - Periódico COM scimago_id
            - SCIMAGO_URL COM valor novo
        QUANDO:
            - Acessarmos a home do periódico
        VERIFICAMOS:
            - Que SIM aparece o link para scimago, com URL diferente
        """
        with current_app.app_context():
            # with
            temp = current_app.config['SCIMAGO_URL']
            current_app.config['SCIMAGO_URL'] = 'https://novaurl/'

            collection = utils.makeOneCollection()
            journal_data = {
                'collection': collection,
                'scimago_id': '22596',
            }
            journal = utils.makeOneJournal(journal_data)
            with self.client as c:
                # when
                response = c.get(
                    url_for('main.journal_detail',
                            url_seg=journal.url_segment))
                response_data = response.data.decode('utf-8')
                # then
                self.assertStatus(response, 200)
                expected = 'https://novaurl/22596'
                self.assertIn(expected, response_data)

                expected = '<a target="_blank" href="{}">Scimago'.format(expected)
                self.assertIn(expected, response_data)
            current_app.config['SCIMAGO_URL'] = temp
