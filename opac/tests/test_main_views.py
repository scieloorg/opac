# coding: utf-8
import unittest
import pathlib
from unittest.mock import patch, Mock
from urllib.parse import urlparse, parse_qs

import flask
import warnings
from flask import url_for, g, current_app
from flask import render_template
from bs4 import BeautifulSoup
from flask_babelex import gettext as _

from .base import BaseTestCase

from . import utils
from webapp.config.lang_names import display_original_lang_name
from webapp.main.views import RetryableError, NonRetryableError


class MainTestCase(BaseTestCase):

    def test_home_page(self):
        """
        Teste da página inicial, deve retorna utf-8 como conjunto de caracter e
        o template ``collection/index.html``.
        """
        with current_app.app_context():
            utils.makeOneCollection()
            with self.client as c:
                response = c.get(url_for('main.index'))
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8', response.content_type)
                self.assert_template_used("collection/index.html")

    def test_should_obtain_the_latest_metric_counts_from_collection(self):
        with current_app.app_context():
            collection = utils.makeOneCollection({
                "metrics" : {
                    "total_journal" : 0,
                    "total_issue" : 0,
                    "total_article" : 0,
                    "total_citation" : 0
                },
            })

            with self.client as client:
                response = client.get(url_for('main.index'))
                collection = g.get('collection')
                self.assertEqual(0, collection.metrics.total_journal)


            utils.makeOneJournal({'is_public': True, 'current_status': 'current'})
            utils.makeOneArticle({'is_public': True})

            with self.client as client:
                response = client.get(url_for('main.index'))
                self.assertEqual(1, collection.metrics.total_article)
                self.assertEqual(1, collection.metrics.total_journal)

    def test_g_object_has_collection_object(self):
        """
        COM:
            - uma nova collection criada com o mesmo acronimo da setting: OPAC_CONFIG
        QUANDO:
            - solicitamo uma pagina
        VERIFICAMOS:
            - que no contexto, a variável 'g' tenha asociado uma instancia da collection
        """

        with current_app.app_context():
            # with
            collection_db_record = utils.makeOneCollection()

            # when
            with self.client as c:
                response = c.get(url_for('main.index'))
                # then
                self.assertStatus(response, 200)
                self.assertTrue(hasattr(g, 'collection'))
                g_collection = g.get('collection')
                self.assertEqual(g_collection._id, collection_db_record._id)

    def test_change_set_locale(self):
        """
        Teste para alterar o idioma da interface, nesse teste a URL:
        '/set_locale/<string:lang_code>' deve criar uma variável na sessão com
        o valor informado.
        """

        with self.client as c:
            response = c.get(url_for('main.set_locale', lang_code='es'))
            self.assertEqual(302, response.status_code)
            self.assertEqual(flask.session['lang'], 'es')

    def test_redirect_when_change_set_locale(self):
        """
        Teste para verificar se o redirecionamento da ``view function``
        ``set_locale`` retorna para a página esperada.
        """

        with self.client as c:
            response = c.get(url_for('main.set_locale', lang_code='es'),
                             headers={'Referer': '/journals/alpha'},
                             follow_redirects=True)
            self.assertStatus(response, 200)

            self.assertTemplateUsed('collection/list_journal.html')

    def test_change_set_locale_with_unknow_lang(self):
        """
        Teste para alterar o idioma da interface, nesse teste a URL:
        '/set_locale/<string:lang_code>' deve retornar uma página com
        ``status_code``400 e manter o idioma padrão ``pt_BR``.
        """
        expected_message = '<p>Código de idioma inválido</p>'

        with self.client as c:
            response = c.get(url_for('main.set_locale', lang_code='en_US'))
            self.assertEqual(400, response.status_code)
            self.assertIn('Código de idioma inválido',
                          response.data.decode('utf-8'))
            self.assertTemplateUsed('errors/400.html')

            self.assertEqual(expected_message,
                             self.get_context_variable('message'))

    @unittest.skip("Revisar/Refazer, agora a lista é carregada com ajax")
    def test_collection_list_alpha(self):
        """
        Teste para avaliar o retorno da ``view function`` collection_list_alpha,
        ao cadastrarmos 10 periódico a interface deve retornar uma listagem
        contendo elementos esperado também deve retornar o template
        ``collection/list_alpha.html``.
        """
        utils.makeOneCollection()
        journals = utils.makeAnyJournal(items=10)

        response = self.client.get(url_for('main.collection_list') + '#alpha')

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_journal.html')

        for journal in journals:
            self.assertIn('journals/%s' % journal.id,
                          response.data.decode('utf-8'))

        self.assertListEqual(sorted([journal.id for journal in journals]),
                             sorted([journal.id for journal in self.get_context_variable('journals')]))

    def test_collection_list_alpha_without_journals(self):
        """
        Teste para avaliar o retorno da ``view function`` collection_list_alpha
        quando não existe periódicos cadastrados deve retorna a msg
        ``Nenhum periódico encontrado`` no corpo da resposta.
        """

        utils.makeOneCollection()
        response = self.client.get(url_for('main.collection_list'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_journal.html')

        self.assertIn('Nenhum periódico encontrado',
                      response.data.decode('utf-8'))

    @unittest.skip("Revisar/Refazer, agora a lista é carregada com ajax")
    def test_collection_list_theme(self):
        """
        Teste para avaliar o retorno da ``view function`` collection_list_theme
        ao cadastrarmos 60 periódico a interface deve retornar uma listagem
        contendo elementos esperado tambémdeve retornar o template
        ``collection/list_theme.html``.
        """

        utils.makeOneCollection()
        journals = utils.makeAnyJournal(items=30,
                                        attrib={"study_areas": ["Engineering"]})
        journals = utils.makeAnyJournal(items=30,
                                        attrib={"study_areas": ["Human Sciences",
                                                "Biological Sciences", "Engineering"]})

        response = self.client.get(url_for('main.collection_list') + '#theme')

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_journal.html')

        for journal in journals:
            self.assertIn('journals/%s' % journal.id,
                          response.data.decode('utf-8'))

    def test_collection_list_theme_without_journals(self):
        """
        Teste para avaliar o retorno da ``view function`` collection_list_theme
        quando não existe periódicos cadastrados deve retorna a msg
        ``Nenhum periódico encontrado`` no corpo da resposta.
        """

        utils.makeOneCollection()
        response = self.client.get(url_for('main.collection_list'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_journal.html')

        self.assertIn('Nenhum periódico encontrado',
                      response.data.decode('utf-8'))

    @unittest.skip("Revisar/Refazer, agora a lista é carregada com ajax")
    def test_collection_list_institution(self):
        """
        Teste para a ``view function`` collection_list_institution, será avaliado
        somente o template utilizado pois essa função depende de definição do atributo
        instituição no manager.
        """

        utils.makeOneCollection()
        warnings.warn("Necessário definir o atributo instituição no modelo do Manager")

        response = self.client.get(url_for('main.collection_list') + '#publisher')

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_journal.html')

    def test_collection_list_institution_without_journals(self):
        """
        Teste para avaliar o retorno da ``view function`` collection_list_institution
        quando não existe periódicos cadastrados deve retorna a msg
        ``Nenhum periódico encontrado`` no corpo da resposta.
        """

        utils.makeOneCollection()
        response = self.client.get(url_for('main.collection_list'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_journal.html')

        self.assertIn('Nenhum periódico encontrado',
                      response.data.decode('utf-8'))

    def test_collection_list_feed(self):
        """
        Teste para verificar a reposta da ``view funciton``collection_list_feed
        Se cadastra 10 periódicos, deve retornar na interface do rss, utilizando
        o template ``collection/list_feed_content.html```.
        """

        with current_app.app_context():

            utils.makeOneCollection()
            journals = utils.makeAnyJournal(items=10)
            issues = []

            for journal in journals:
                issue = utils.makeOneIssue({'journal': journal.id})
                utils.makeAnyArticle(
                    issue=issue,
                    attrib={'journal': journal.id, 'issue': issue.id}
                )
                issues.append(issue)

            response = self.client.get(url_for('main.collection_list_feed'))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('collection/list_feed_content.html')

            for journal in journals:
                self.assertIn('%s' % journal.url_segment,
                              response.data.decode('utf-8'))

            for issue in issues:
                self.assertIn('%s' % issue.url_segment,
                              response.data.decode('utf-8'))

    def test_collection_list_feed_without_journals(self):
        """
        Teste para avaliar o retorno da ``view function`` collection_list_feed
        quando não existe periódicos cadastrados deve retorna a msg
        ``Nenhum periódico encontrado`` no corpo da resposta.
        """
        with current_app.app_context():

            utils.makeOneCollection()

            response = self.client.get(url_for('main.collection_list_feed'))

            self.assertStatus(response, 200)
            self.assertIn('Nenhum periódico encontrado',
                          response.data.decode('utf-8'))

    def test_collection_list_feed_without_issues(self):
        """
        Teste para verificar a reposta da ``view funciton``collection_list_feed
        Se cadastra 10 periódicos sem número, deve retornar na interface do
        rss, utilizando o template ``collection/list_feed_content.html```.
        """

        with current_app.app_context():

            utils.makeOneCollection()
            journals = utils.makeAnyJournal(items=10)

            response = self.client.get(url_for('main.collection_list_feed'))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('collection/list_feed_content.html')

            for journal in journals:
                self.assertIn('%s' % journal.url_segment,
                              response.data.decode('utf-8'))

    def test_journal_feed(self):
        """
        Teste da ``view function`` ``journal_feed``, deve retornar um rss
        que usa o template ``issue/feed_content.html`` e o título do periódico no
        corpo da página.
        """

        with current_app.app_context():
            utils.makeOneCollection()
            journal = utils.makeOneJournal({'title': 'Revista X'})
            issue = utils.makeOneIssue({'journal': journal})
            utils.makeAnyArticle(
                issue=issue,
                attrib={
                        'journal': journal.id,
                        'issue': issue.id}
            )

            response = self.client.get(url_for('main.journal_feed',
                                               url_seg=journal.url_segment))

            self.assertTrue(200, response.status_code)
            self.assertTemplateUsed('issue/feed_content.html')

    def test_journal_feed_has_doi(self):
        """
        Teste da ``view function`` ``journal_feed``, deve retornar um rss
        que usa o template ``issue/feed_content.html`` e os respectivos artigo com DOI.
        """

        with current_app.app_context():
            utils.makeOneCollection()
            journal = utils.makeOneJournal({'title': 'Revista X'})
            issue = utils.makeOneIssue({'journal': journal})
            utils.makeAnyArticle(
                issue=issue,
                attrib={
                        'journal': journal.id,
                        'issue': issue.id,
                        'doi': '10.2105/AJPH.2009.160184'
                       }
            )

            response = self.client.get(url_for('main.journal_feed',
                                               url_seg=journal.url_segment))

            self.assertTrue(200, response.status_code)
            self.assertTemplateUsed('issue/feed_content.html')
            self.assertIn('<id>10.2105/AJPH.2009.160184</id>', response.data.decode('utf-8'))

    def test_journal_feed_with_unknow_id(self):
        """
        Teste da ``view function`` ``journal_feed`` com um id desconhecido
        deve retornar uma página com ``status_code`` 404 e msg
        ``Periódico não encontrado``.
        """

        utils.makeAnyJournal(items=6)

        unknow_id = '0k2qhs8slwnui8'

        response = self.client.get(url_for('main.journal_feed',
                                   url_seg=unknow_id))

        self.assertStatus(response, 404)
        self.assertIn('Periódico não encontrado',
                      response.data.decode('utf-8'))

    def test_journal_feed_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``journal_feed`` acessando um periódico
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """
        unpublish_reason = 'plágio'
        journal = utils.makeOneJournal({
            'is_public': False,
            'unpublish_reason': unpublish_reason})

        response = self.client.get(url_for('main.journal_feed',
                                           url_seg=journal.url_segment))

        self.assertStatus(response, 404)
        self.assertIn(unpublish_reason, response.data.decode('utf-8'))

    # ISSUE

    def test_issue_feed(self):
        """
        Teste da ``view function`` ``issue_feed``, deve retornar um rss
        que usa o template ``issue/feed_content.html`` e o título do periódico no
        corpo da página.
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'number': '31',
                                        'volume': '10',
                                        'journal': journal})
            utils.makeAnyArticle(
                issue=issue,
                attrib={'journal': issue.journal.id, 'issue': issue.id}
            )

            response = self.client.get(url_for('main.issue_feed',
                                       url_seg=journal.url_segment,
                                       url_seg_issue=issue.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/feed_content.html')
            self.assertIn('Vol. 10 No. 31', response.data.decode('utf-8'))

    def test_issue_feed_has_doi(self):
        """
        Teste da ``view function`` ``issue_feed``, deve retornar um rss
        que usa o template ``issue/feed_content.html`` e os respectivos artigo com DOI.
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'number': '31',
                                        'volume': '10',
                                        'journal': journal})
            utils.makeAnyArticle(
                issue=issue,
                attrib={
                        'journal': issue.journal.id,
                        'issue': issue.id,
                        'doi': '10.2105/AJPH.2009.160184'}
            )

            response = self.client.get(url_for('main.issue_feed',
                                       url_seg=journal.url_segment,
                                       url_seg_issue=issue.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/feed_content.html')
            self.assertIn('<id>10.2105/AJPH.2009.160184</id>', response.data.decode('utf-8'))

    def test_issue_feed_unknow_issue_id(self):
        """
        Teste para avaliar o retorno da ``view function`` ``issue_feed``
        quando é acessado utilizando um identificador do issue desconhecido,
        deve retorna status_code 404 com a msg ``Número não encontrado``.
        """
        journal = utils.makeOneJournal()

        utils.makeOneIssue({'journal': journal})

        unknow_url_seg = '2015.v6n3'

        response = self.client.get(url_for('main.issue_feed',
                                   url_seg=journal.url_segment,
                                   url_seg_issue=unknow_url_seg))

        self.assertStatus(response, 404)
        self.assertIn('Número não encontrado', response.data.decode('utf-8'))

    def test_issue_feed_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_feed`` acessando um número
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """

        unpublish_reason = 'número incorreto'
        journal = utils.makeOneJournal()
        issue = utils.makeOneIssue({
            'is_public': False,
            'unpublish_reason': unpublish_reason,
            'journal': journal})

        response = self.client.get(url_for('main.issue_feed',
                                           url_seg=journal.url_segment,
                                           url_seg_issue=issue.url_segment))

        self.assertStatus(response, 404)
        self.assertIn('número incorreto', response.data.decode('utf-8'))

    def test_issue_feed_with_journal_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando um número
        com atributo is_public=True, porém com um periódico com atributo
        is_public=False deve retorna uma página com ``status_code`` 404 e msg
        cadastrada no atributo ``reason`` do periódico.
        """
        unpublish_reason = 'Revista removida da coleção'
        journal = utils.makeOneJournal({
            'is_public': False,
            'unpublish_reason': unpublish_reason})
        issue = utils.makeOneIssue({
            'is_public': True,
            'journal': journal.id})

        response = self.client.get(url_for('main.issue_feed',
                                           url_seg=journal.url_segment,
                                           url_seg_issue=issue.url_segment))

        self.assertStatus(response, 404)
        self.assertIn(unpublish_reason, response.data.decode('utf-8'))

    # ARTICLE

    def test_article_detail_v3(self):
        """
        Teste da ``view function`` ``article_detail_v3``, deve retornar uma página
        que usa o template ``article/detail.html``.
        """
        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            article = utils.makeOneArticle({'title': 'Article Y',
                                            'original_language': 'en',
                                            'languages': ['es', 'pt'],
                                            'translated_titles': [
                                                {'language': 'es', 'name': u'Artículo en español'},
                                                {'language': 'pt', 'name': u'Artigo en Português'},
                                            ],
                                            'issue': issue,
                                            'journal': journal,
                                            'url_segment': '10-11'})

            response = self.client.get(url_for('main.article_detail_v3',
                                               url_seg=journal.url_segment,
                                               article_pid_v3=article.aid))

            self.assertStatus(response, 200)

    def test_article_detail_v3_redirects_to_original_language(self):
        """
        Teste da ``view function`` ``article_detail_v3``, deve retornar uma página
        que usa o template ``article/detail.html``.
        """
        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            article = utils.makeOneArticle({'title': 'Article Y',
                                            'original_language': 'en',
                                            'languages': ['es', 'pt'],
                                            'translated_titles': [
                                                {'language': 'es', 'name': u'Artículo en español'},
                                                {'language': 'pt', 'name': u'Artigo en Português'},
                                            ],
                                            'issue': issue,
                                            'journal': journal,
                                            'url_segment': '10-11'})

            response = self.client.get(url_for('main.article_detail_v3',
                                               url_seg=journal.url_segment,
                                               article_pid_v3=article.aid,
                                               lang='ru'))

            self.assertRedirects(
                response,
                url_for(
                    'main.article_detail_v3',
                    url_seg=journal.url_segment,
                    article_pid_v3=article.aid,
                    format='html',
                )
            )

    def test_article_detail_pid_redirect(self):
        """
        Teste da ``view function`` ``article_detail_pid``, verifica somente o
        redirecionamento.
        """
        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            utils.makeOneArticle({'title': 'Article Y',
                                  'issue': issue,
                                  'journal': journal,
                                  'pid': 'S0102-311X2018000100101',
                                  'url_segment': '10-11'})

            response = self.client.get(url_for('main.article_detail_pid',
                                               pid='S0102-311X2018000100101'))

            #TODO: Alterar o código para 301 (Movido Permanentemente)
            self.assertStatus(response, 302)

    def test_article_detail_pid_redirect_follow(self):
        """
        Teste da ``view function`` ``article_detail_pid``,
        deve retornar uma página que usa o template ``article/detail.html``.
        """
        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            article = utils.makeOneArticle({'title': 'Article Y',
                                            'issue': issue,
                                            'journal': journal,
                                            'pid': 'S0102-311X2018000100101',
                                            'url_segment': '10-11'})

            response = self.client.get(url_for('main.article_detail_pid',
                                               pid='S0102-311X2018000100101'),
                                       follow_redirects=True)

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')
            self.assertEqual(self.get_context_variable('article').id, article.id)
            self.assertEqual(self.get_context_variable('journal').id, article.journal.id)
            self.assertEqual(self.get_context_variable('issue').id, article.issue.id)

    @patch('requests.get')
    def test_article_detail_v3_translate_version_(self, mocked_requests_get):
        """
        Teste da ``view function`` ``article_detail_v3``, deve retornar uma página
        que usa o template ``article/detail.html``.
        """
        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b'<html/>'
        mocked_requests_get.return_value = mocked_response

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            article = utils.makeOneArticle({'title': 'Article Y',
                                            'issue': issue,
                                            'journal': journal,
                                            'url_segment': '10-11',
                                            'htmls': [
                                                {'lang': 'de', 'url': 'https://link/de_artigo.html'},
                                                {'lang': 'pt', 'url': 'https://link/pt_artigo.html'},
                                                {'lang': 'bla', 'url': 'https://link/bla_artigo.html'},
                                                ]
                                            })

            response = self.client.get(url_for('main.article_detail_v3',
                                               url_seg=journal.url_segment,
                                               article_pid_v3=article.aid,
                                               lang='pt'))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')
            content = response.data.decode('utf-8')

            urls = {html['lang']: url_for(
                                   'main.article_detail_v3',
                                   url_seg=journal.url_segment,
                                   article_pid_v3=article.aid,
                                   lang=html['lang'])
                    for html in article.htmls
                    }
            self.assertIn('{}">Deutsch<'.format(urls['de']), content)
            self.assertIn('{}">bla<'.format(urls['bla']), content)
            self.assertIn('{}">Português<'.format(urls['pt']), content)
            self.assertEqual(
                content.count('{}">Deutsch<'.format(urls['de'])), 1)
            self.assertEqual(
                content.count('{}">Português<'.format(urls['pt'])), 1)
            self.assertEqual(
                content.count('{}">bla<'.format(urls['bla'])), 1)

    @patch('requests.get')
    def test_article_detail_v3_has_citation_title_in_pt(self, mocked_requests_get):
        """
        Teste da ``view function`` ``article_detail_v3``, deve retornar uma página
        que usa o template ``article/detail.html``.
        """
        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b'<html/>'
        mocked_requests_get.return_value = mocked_response

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            article = utils.makeOneArticle({'title': 'Article Y',
                                            'original_language': 'en',
                                            'languages': ['es', 'pt'],
                                            'translated_titles': [
                                                {'language': 'es', 'name': u'Artículo título'},
                                                {'language': 'pt', 'name': u'Artigo título'},
                                            ],
                                            'issue': issue,
                                            'journal': journal,
                                            'url_segment': '10-11',
                                            'htmls': [
                                                {'lang': 'es', 'url': 'https://link/es_artigo.html'},
                                                {'lang': 'de', 'url': 'https://link/de_artigo.html'},
                                                {'lang': 'pt', 'url': 'https://link/pt_artigo.html'},
                                                {'lang': 'bla', 'url': 'https://link/bla_artigo.html'},
                                                ]
                                            })

            response = self.client.get(url_for('main.article_detail_v3',
                                               url_seg=journal.url_segment,
                                               article_pid_v3=article.aid,
                                               lang='pt'))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')
            content = response.data.decode('utf-8')

            self.assertIn(
                '<meta name="citation_language" content="pt"></meta>',
                content
            )
            self.assertIn(
                u'<meta name="citation_title" content="Artigo título"></meta>',
                content
            )

    @patch('requests.get')
    def test_article_detail_v3_has_citation_title_in_es(self, mocked_requests_get):
        """
        Teste da ``view function`` ``article_detail_v3``, deve retornar uma página
        que usa o template ``article/detail.html``.
        """
        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b'<html/>'
        mocked_requests_get.return_value = mocked_response

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            article = utils.makeOneArticle({'title': 'Article Y',
                                            'original_language': 'en',
                                            'languages': ['es', 'pt'],
                                            'translated_titles': [
                                                {'language': 'es', 'name': u'Título del Artículo'},
                                                {'language': 'pt', 'name': u'Título do Artigo'},
                                            ],
                                            'issue': issue,
                                            'journal': journal,
                                            'url_segment': '10-11',
                                            'htmls': [
                                                {'lang': 'es', 'url': 'https://link/es_artigo.html'},
                                                {'lang': 'pt', 'url': 'https://link/pt_artigo.html'},
                                                {'lang': 'de', 'url': 'https://link/de_artigo.html'},
                                                {'lang': 'bla', 'url': 'https://link/bla_artigo.html'},
                                                ]
                                            })

            response = self.client.get(url_for('main.article_detail_v3',
                                               url_seg=journal.url_segment,
                                               article_pid_v3=article.aid,
                                               lang='es'))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')
            content = response.data.decode('utf-8')
            self.assertIn(
                '<meta name="citation_language" content="es"></meta>',
                content
            )
            self.assertIn(
                u'<meta name="citation_title" content="Título del Artículo"></meta>',
                content
            )

    def test_article_detail_v3_links_to_gscholar(self):
        """
        Teste da ``view function`` ``article_detail_v3``, deve retornar uma página
        que usa o template ``article/detail.html``.
        """
        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal({"title":"Título do periódico"})

            issue = utils.makeOneIssue({'journal': journal})

            article = utils.makeOneArticle({'title': 'Article Y',
                                            'issue': issue,
                                            'journal': journal,
                                            'url_segment': '10-11'})

            response = self.client.get(url_for('main.article_detail_v3',
                                               url_seg=journal.url_segment,
                                               article_pid_v3=article.aid,
                                               lang='pt'))

            self.assertStatus(response, 200)
            page_content = response.data.decode('utf-8')
            self.assertTemplateUsed('article/detail.html')
            self.assertEqual(self.get_context_variable('article').id, article.id)
            self.assertEqual(self.get_context_variable('journal').id, article.journal.id)
            self.assertEqual(self.get_context_variable('issue').id, article.issue.id)
            result = self.get_context_variable('related_links')
            self.assertEqual(result[0][0], 'Google')
            self.assertEqual(result[1][0], 'Google Scholar')
            self.assertIn('Article Y', result[0][2])
            self.assertIn('Article Y', result[1][2])
            self.assertIn('Google', page_content)
            self.assertIn('/scholar', page_content)

    def test_article_detail_v3_links_to_gscholar_for_article_without_title(self):
        """
        Teste da ``view function`` ``article_detail_v3``, deve retornar uma página
        que usa o template ``article/detail.html``.
        """
        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal({"title":"Título do periódico"})

            issue = utils.makeOneIssue({'journal': journal})

            article = utils.makeOneArticle({'issue': issue,
                                            'journal': journal,
                                            'url_segment': '10-11'})

            response = self.client.get(url_for('main.article_detail_v3',
                                               url_seg=journal.url_segment,
                                               article_pid_v3=article.aid,
                                               lang='pt'))

            self.assertStatus(response, 200)
            page_content = response.data.decode('utf-8')
            self.assertTemplateUsed('article/detail.html')
            self.assertEqual(self.get_context_variable('article').id, article.id)
            self.assertEqual(self.get_context_variable('journal').id, article.journal.id)
            self.assertEqual(self.get_context_variable('issue').id, article.issue.id)
            result = self.get_context_variable('related_links')
            self.assertEqual(result[0][0], 'Google')
            self.assertEqual(result[1][0], 'Google Scholar')
            self.assertIn(journal.title, result[0][2])
            self.assertIn(journal.title, result[1][2])
            self.assertIn('Google', page_content)
            self.assertIn('/scholar', page_content)

    def test_legacy_url_aop_article_detail(self):
        """
        Teste da ``view function`` ``router_legacy``, deve retornar uma página
        que usa o template ``article/detail.html``.
        """
        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            aop_pid = '1111-11111111111111111'

            article = utils.makeOneArticle({'title': 'Article Y',
                                            'issue': issue,
                                            'journal': journal,
                                            'url_segment': '10-11',
                                            'aop_pid': aop_pid})

            url = '%s?script=sci_arttext&pid=%s' % (
                url_for('main.router_legacy'), aop_pid)

            response = self.client.get(url, follow_redirects=True)

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')
            self.assertEqual(self.get_context_variable('article').id, article.id)
            self.assertEqual(self.get_context_variable('journal').id, article.journal.id)
            self.assertEqual(self.get_context_variable('issue').id, article.issue.id)

    def test_legacy_url_aop_article_detail_wrong_aop_pid(self):
        """
        Teste da ``view function`` ``router_legacy``, deve retornar uma página
        que usa o template ``article/detail.html``.
        """
        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            utils.makeOneArticle({'title': 'Article Y',
                                  'issue': issue,
                                  'journal': journal,
                                  'url_segment': '10-11',
                                  'aop_pid': '1111-11111111111111110'})

            url = '%s?script=sci_arttext&pid=%s' % (
                url_for('main.router_legacy'), '1111-11111111111111111')

            response = self.client.get(url)

            self.assertStatus(response, 404)
            self.assertIn('Artigo não encontrado', response.data.decode('utf-8'))

    @unittest.skip(u'precisa de integração com SSM para retornar o SSM')
    def test_legacy_url_pdf_article_detail(self):
        """
        Teste da view ``router_legacy``, deve retornar uma página de pdf quando
        na querystring tem: ?script=sci_pdf&pid={PID VALIDO}
        e que usa o template ``article/detail_pdf.html``.
        """
        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            pid = '1111-11111111111111111'

            article = utils.makeOneArticle({'title': 'Article Y',
                                            'issue': issue,
                                            'journal': journal,
                                            'url_segment': '10-11',
                                            'pid': pid})

            url = '%s?script=sci_pdf&pid=%s' % (
                url_for('main.router_legacy'), pid)

            response = self.client.get(url)

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail_pdf.html')
            self.assertEqual(self.get_context_variable('article').id, article.id)
            self.assertEqual(self.get_context_variable('journal').id, article.journal.id)
            self.assertEqual(self.get_context_variable('issue').id, article.issue.id)

    def test_legacy_url_pdf_article_detail_wrong_pid(self):
        """
        Teste da view ``router_legacy``, deve retornar uma página de erro (404 not found)
        na querystring tem: ?script=sci_pdf&pid={PID INVALIDO}
        """
        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            valid_pid = '1111-11111111111111111'
            invalid_pid = 'ABCD-22222222222222222'

            utils.makeOneArticle({
                'title': 'Article Y',
                'issue': issue,
                'journal': journal,
                'url_segment': '10-11',
                'pid': valid_pid})

            url = '%s?script=sci_pdf&pid=%s' % (
                url_for('main.router_legacy'), invalid_pid)

            response = self.client.get(url)

            self.assertStatus(response, 404)
            self.assertIn('Artigo não encontrado', response.data.decode('utf-8'))

    def test_legacy_url_article_detail_pid_not_found(self):
        """
        Teste da view ``router_legacy_article``, deve retornar uma página de erro (404 not found)
        na querystring tem: ?pid={PID INVALIDO}
        """
        with current_app.app_context():
            utils.makeOneCollection()
            journal = utils.makeOneJournal()
            issue = utils.makeOneIssue({'journal': journal})
            valid_pid = '1111-11111111111111111'
            invalid_pid = 'ABCD-22222222222222222'

            utils.makeOneArticle({
                'title': 'Article Y',
                'issue': issue,
                'journal': journal,
                'pid': valid_pid})

            url = '%s?pid=%s&lng=en' % (
                url_for('main.router_legacy_article', text_or_abstract="fbtext"),
                invalid_pid
            )

            response = self.client.get(url)

            self.assertStatus(response, 404)
            self.assertIn('Artigo não encontrado', response.data.decode('utf-8'))

    def test_legacy_url_article_detail_no_public_article(self):
        """
        Teste da view ``router_legacy_article``, deve retornar uma página de erro (404 not found)
        para artigo não público
        """
        with current_app.app_context():
            utils.makeOneCollection()
            journal = utils.makeOneJournal()
            issue = utils.makeOneIssue({'journal': journal})
            v1_pid = '0101-0101(99)123456'
            v2_pid = '1111-11111111111111111'
            utils.makeOneArticle({
                'title': 'Article Y',
                'issue': issue,
                'journal': journal,
                'is_public': False,
                'pid': v2_pid,
                'scielo_pids': {
                    'v1': v1_pid,
                    'v2': v2_pid,
                }
            })

            url = '%s?pid=%s&lng=en' % (
                url_for('main.router_legacy_article', text_or_abstract="fbtext"),
                v1_pid
            )
            response = self.client.get(url)

            self.assertStatus(response, 404)
            self.assertIn('Artigo não encontrado', response.data.decode('utf-8'))

    def test_legacy_url_redirects_to_article_detail_v3(self):
        """
        Teste da view ``router_legacy_article``, deve retornar redirecionar
        para os detalhes do artigo (main.article_detail_v3)
        """
        with current_app.app_context():
            utils.makeOneCollection()
            journal = utils.makeOneJournal()
            issue = utils.makeOneIssue({'journal': journal})
            v1_pid = '0101-0101(99)123456'
            v2_pid = '1111-11111111111111111'
            article = utils.makeOneArticle({
                'title': 'Article Y',
                'issue': issue,
                'journal': journal,
                'url_segment': '10-11',
                'pid': v2_pid,
                'scielo_pids': {
                    'v1': v1_pid,
                    'v2': v2_pid,
                }
            })

            url = '%s?pid=%s&lng=en' % (
                url_for('main.router_legacy_article', text_or_abstract="fbtext"),
                v1_pid
            )
            response = self.client.get(url)
            self.assertRedirects(
                response,
                url_for(
                    'main.article_detail_v3',
                    url_seg=journal.url_segment,
                    article_pid_v3=article.aid,
                ),
            )

    def test_article_detail_v3_without_articles(self):
        """
        Teste para avaliar o retorno da ``view function`` ``article_detail_v3``
        quando não existe artigos cadastrados deve retornar ``status_code`` 404
        e a msg ``Artigo não encontrado``
        """

        journal = utils.makeOneJournal()

        issue = utils.makeOneIssue({'journal': journal})

        response = self.client.get(url_for('main.article_detail_v3',
                                           url_seg=journal.url_segment,
                                           article_pid_v3='unknown-article',
                                           lang='pt'))

        self.assertStatus(response, 404)
        self.assertIn('Artigo não encontrado', response.data.decode('utf-8'))

    def test_article_detail_v3_with_journal_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``article_detail_v3`` acessando um artigo
        com atributo is_public=True, porém com um periódico com atributo
        is_public=False deve retorna uma página com ``status_code`` 404 e msg
        cadastrada no atributo ``reason`` do periódico.
        """
        unpublish_reason = 'Revista removida da coleção'
        journal = utils.makeOneJournal({
            'is_public': False,
            'unpublish_reason': unpublish_reason})

        issue = utils.makeOneIssue({
            'is_public': True,
            'journal': journal})

        article = utils.makeOneArticle({
            'issue': issue,
            'journal': journal})

        response = self.client.get(url_for('main.article_detail_v3',
                                           url_seg=journal.url_segment,
                                           article_pid_v3=article.aid,
                                           lang='pt'))

        self.assertStatus(response, 404)
        self.assertIn(unpublish_reason, response.data.decode('utf-8'))

    def test_article_detail_with_issue_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``article_detail_v3`` acessando um artigo
        com atributo is_public=False, porém com um periódico com atributo
        is_public=True deve retorna uma página com ``status_code`` 404 e msg
        cadastrada no atributo ``reason`` do número.
        """

        unpublish_reason = 'Facículo rejeitado'
        journal = utils.makeOneJournal()
        issue = utils.makeOneIssue({
            'is_public': False,
            'unpublish_reason': unpublish_reason,
            'journal': journal.id})

        article = utils.makeOneArticle({
            'issue': issue.id,
            'journal': journal.id})

        response = self.client.get(url_for('main.article_detail_v3',
                                           url_seg=journal.url_segment,
                                           article_pid_v3=article.aid,
                                           lang='pt'))

        self.assertStatus(response, 404)
        self.assertIn(unpublish_reason, response.data.decode('utf-8'))

    def test_article_detail_with_article_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``article_detail_v3`` acessando um artigo
        com atributo is_public=False, deve retorna uma página com
         ``status_code`` 404 e msg cadastrada no atributo ``reason`` do artigo.
        """

        unpublish_reason = 'Artigo com problemas de licença'
        journal = utils.makeOneJournal()
        issue = utils.makeOneIssue({'journal': journal.id})

        article = utils.makeOneArticle({
            'is_public': False,
            'unpublish_reason': unpublish_reason,
            'issue': issue,
            'journal': journal})

        response = self.client.get(url_for('main.article_detail_v3',
                                           url_seg=journal.url_segment,
                                           article_pid_v3=article.aid,
                                           lang='pt'))

        self.assertStatus(response, 404)

    def test_pdf_url(self):
        """
        Testa se as URLs para os PDFs estão sendo montados com seus respectivos idiomas.

        Exemplo de URL para o PDF: ``/pdf/ssp/2001.v78/e937749/en``
        """

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000', 'acronym': 'cta'},)

            issue = utils.makeOneIssue({
                'journal': journal.id,
                'label': 'v39s2',
                'year': '2009',
                'volume': '39',
                'number': '1',
                'suppl_text': '',
            })

            article = utils.makeOneArticle({
                'journal': journal.id,
                'issue': issue.id,
                'elocation': 'e1',
                'original_language': 'pt',
                'languages': ["es", "en"],
                'pdfs': [
                    {
                        'lang': 'en',
                        'url': 'http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651aen.pdf',
                        'file_path': '/pdf/cta/v39s2/0101-2061-cta-fst30618-en.pdf',
                        'type': 'pdf'
                    },
                    {
                        'lang': 'pt',
                        'url': 'http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651apt.pdf',
                        'file_path': '/pdf/cta/v39s2/0101-2061-cta-fst30618-pt.pdf',
                        'type': 'pdf'
                    },
                    {
                        'lang': 'es',
                        'url': 'http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651aes.pdf',
                        'file_path': '/pdf/cta/v39s2/0101-2061-cta-fst30618-es.pdf',
                        'type': 'pdf'
                    }
                ]
            })

            response = self.client.get(url_for('main.article_detail_v3',
                                               url_seg=journal.url_segment,
                                               article_pid_v3=article.aid,
                                               lang='en'), follow_redirects=False)

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')

            content = response.data.decode('utf-8')
            #TODO: Há maneira melhor de executar estas asserções?
            self.assertTrue(
                '/j/cta/a/%s/?lang=en&amp;format=pdf' % article.aid in content or '/j/cta/a/%s/?format=pdf&amp;lang=en' % article.aid in content
            )
            self.assertTrue(
                '/j/cta/a/%s/?lang=pt&amp;format=pdf' % article.aid in content or '/j/cta/a/%s/?format=pdf&amp;lang=pt' % article.aid in content
            )
            self.assertTrue(
                '/j/cta/a/%s/?lang=es&amp;format=pdf' % article.aid in content or '/j/cta/a/%s/?format=pdf&amp;lang=es' % article.aid in content
            )

    def test_pdf_url_redirects_to_original_language(self):
        """
        Testa se as URLs para os PDFs estão sendo montados com seus respectivos idiomas.

        Exemplo de URL para o PDF: ``/pdf/ssp/2001.v78/e937749/en``
        """

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000', 'acronym': 'cta'},)

            issue = utils.makeOneIssue({
                'journal': journal.id,
                'label': 'v39s2',
                'year': '2009',
                'volume': '39',
                'number': '1',
                'suppl_text': '',
            })

            article = utils.makeOneArticle({
                'journal': journal.id,
                'issue': issue.id,
                'elocation': 'e1',
                'pdfs': [
                    {
                        'lang': 'en',
                        'url': 'http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651aen.pdf',
                        'file_path': '/pdf/cta/v39s2/0101-2061-cta-fst30618-en.pdf',
                        'type': 'pdf'
                    },
                    {
                        'lang': 'pt',
                        'url': 'http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651apt.pdf',
                        'file_path': '/pdf/cta/v39s2/0101-2061-cta-fst30618-pt.pdf',
                        'type': 'pdf'
                    },
                    {
                        'lang': 'es',
                        'url': 'http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651aes.pdf',
                        'file_path': '/pdf/cta/v39s2/0101-2061-cta-fst30618-es.pdf',
                        'type': 'pdf'
                    }
                ]
            })

            response = self.client.get(url_for('main.article_detail_v3',
                                               url_seg=journal.url_segment,
                                               article_pid_v3=article.aid,
                                               format='pdf',
                                               lang='ru'), follow_redirects=False)

            self.assertStatus(response, 301)

    @patch("webapp.main.views.fetch_data")
    def test_xml_url_redirect_to_xml_with_original_language(self, mk_fetch_data):
        """
        Testa se as URLs para os XMLs estão sendo montados com o idioma original do artigo,
        quando existir o param ``lang``.

        Formato da URL para o teste: ``/j/<acron>/a/<article_pid_v3>/?format=xml&lang=<lang>``
        """

        test_xml_path = pathlib.Path("opac/tests/fixtures/document.xml")
        mk_fetch_data.return_value = test_xml_path.read_bytes()

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000', 'acronym': 'cta'},)

            issue = utils.makeOneIssue({
                'journal': journal.id,
                'label': 'v39s2',
                'year': '2009',
                'volume': '39',
                'number': '1',
                'suppl_text': '',
            })

            article = utils.makeOneArticle({
                'journal': journal.id,
                'issue': issue.id,
                'elocation': 'e1',
                'original_language': 'pt',
                'languages': ["es", "en", "pt"],
                'xml': "https://kernel:6543/documents/kSiec9encE0f2dp"
            })

            response = self.client.get(url_for('main.article_detail_v3',
                                               url_seg=journal.url_segment,
                                               article_pid_v3=article.aid,
                                               format='xml',
                                               lang="pt"))

            self.assertStatus(response, 200)
            self.assertEqual(test_xml_path.read_bytes(), response.data)

    @patch("webapp.main.views.fetch_data")
    def test_xml_ok(self, mk_fetch_data):
        """
        Testa se retorna XML para ``format=xml``.

        Formato da URL para o teste: ``/j/<acron>/a/<article_pid_v3>/?format=xml``
        """

        test_xml_path = pathlib.Path("opac/tests/fixtures/document.xml")
        mk_fetch_data.return_value = test_xml_path.read_bytes()

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000', 'acronym': 'cta'},)

            issue = utils.makeOneIssue({
                'journal': journal.id,
                'label': 'v39s2',
                'year': '2009',
                'volume': '39',
                'number': '1',
                'suppl_text': '',
            })

            article = utils.makeOneArticle({
                'journal': journal.id,
                'issue': issue.id,
                'elocation': 'e1',
                'original_language': 'pt',
                'languages': ["es", "en"],
                'xml': "https://kernel:6543/documents/kSiec9encE0f2dp"
            })

            response = self.client.get(url_for('main.article_detail_v3',
                                               url_seg=journal.url_segment,
                                               article_pid_v3=article.aid,
                                               format='xml'))

            self.assertStatus(response, 200)
            self.assertEqual(test_xml_path.read_bytes(), response.data)

    @patch("webapp.main.views.render_html")
    def test_when_render_html_raises_a_non_retryable_error_it_should_return_a_status_code_404(
        self, mk_render_html
    ):
        mk_render_html.side_effect = NonRetryableError

        with current_app.app_context():
            utils.makeOneCollection()
            journal = utils.makeOneJournal()
            issue = utils.makeOneIssue({"journal": journal})
            article = utils.makeOneArticle(
                {
                    "title": "A",
                    "original_language": "en",
                    "issue": issue,
                    "journal": journal,
                    "url_segment": "10",
                }
            )

            response = self.client.get(
                url_for(
                    "main.article_detail_v3",
                    url_seg=journal.url_segment,
                    article_pid_v3=article.aid,
                )
            )

            self.assertStatus(response, 404)


    @patch("webapp.main.views.render_html")
    def test_when_render_html_raises_a_retryable_error_the_article_detail_v3_should_return_a_status_code_500(
        self, mk_render_html
    ):
        mk_render_html.side_effect = RetryableError

        with current_app.app_context():
            utils.makeOneCollection()
            journal = utils.makeOneJournal()
            issue = utils.makeOneIssue({"journal": journal})
            article = utils.makeOneArticle(
                {
                    "title": "A",
                    "original_language": "en",
                    "issue": issue,
                    "journal": journal,
                    "url_segment": "10",
                }
            )

            response = self.client.get(
                url_for(
                    "main.article_detail_v3",
                    url_seg=journal.url_segment,
                    article_pid_v3=article.aid,
                )
            )

            self.assertStatus(response, 500)

    @patch("webapp.main.views.fetch_data")
    def test_when_fetch_data_raises_a_retryable_error_the_article_detail_v3_should_return_a_500_status_code(
        self, mk_fetch_data
    ):

        mk_fetch_data.side_effect = RetryableError

        with current_app.app_context():
            utils.makeOneCollection()
            journal = utils.makeOneJournal()
            issue = utils.makeOneIssue({"journal": journal})
            article = utils.makeOneArticle(
                {
                    "title": "A",
                    "original_language": "en",
                    "issue": issue,
                    "journal": journal,
                    "url_segment": "10",
                    "pdfs": [
                        {
                            "lang": "en",
                            "url": "http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651aen.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618-en.pdf",
                            "type": "pdf"
                        },
                    ]
                }
            )

            response = self.client.get(
                url_for(
                    "main.article_detail_v3",
                    url_seg=journal.url_segment,
                    article_pid_v3=article.aid,
                    format="pdf",
                    lang="en",
                ),
                follow_redirects=False
            )

            self.assertStatus(response, 500)

    # HOMEPAGE

    def test_collection_sponsors_at_homepage(self):
        """
        acessar na homepage deve mostrar os sponsors no rodapé
        """
        # with
        with current_app.app_context():
            collection = utils.makeOneCollection()
            sponsor1 = utils.makeOneSponsor(
                {
                    'order': 0,
                    'name': 'spo1',
                    'url': 'http://sponsor1.com',
                    'logo_url': 'http://sponsor1.com/logo1.png'
                }
            )
            sponsor2 = utils.makeOneSponsor(
                {
                    'order': 1,
                    'name': 'spo2',
                    'url': 'http://sponsor2.com',
                    'logo_url': 'http://sponsor2.com/logo1.png'
                }
            )
            sponsor3 = utils.makeOneSponsor(
                {
                    'order': 2,
                    'name': 'spo3',
                    'url': 'http://sponsor2.com',
                    'logo_url': 'http://sponsor2.com/logo1.png'
                }
            )
            collection.sponsors = [
                sponsor1,
                sponsor2,
                sponsor3,
            ]
            collection.save()
            # when
            response = self.client.get(url_for('main.index'))
            # then
            self.assertStatus(response, 200)
            self.assertIn('<div class="partners">', response.data.decode('utf-8'))
            self.assertIn('"/about/"', response.data.decode('utf-8'))
            self.assertNotIn(
                '/collection/about/', response.data.decode('utf-8'))

            for sponsor in [sponsor1, sponsor2, sponsor3]:
                self.assertIn(sponsor.name, response.data.decode('utf-8'))
                self.assertIn(sponsor.url, response.data.decode('utf-8'))
                self.assertIn(sponsor.logo_url, response.data.decode('utf-8'))

    def test_collection_address_at_homepage_footer(self):
        """
        acessar na homepage deve mostrar o endereço da coleção
        """
        # with
        with current_app.app_context():
            collection_data = {
                'address1': 'foo address',
                'address2': 'foo address',
            }
            collection = utils.makeOneCollection(attrib=collection_data)
            # when
            response = self.client.get(url_for('main.index'))
            # then
            self.assertStatus(response, 200)
            self.assertIn(collection['address1'], response.data.decode('utf-8'))
            self.assertIn(collection['address2'], response.data.decode('utf-8'))

    def test_collection_address_at_about_page_footer(self):
        """
        acessar na pagina Sobre o SciELO deve mostrar o endereço da coleção
        """
        # with
        with current_app.app_context():
            collection_data = {
                'address1': 'foo address',
                'address2': 'foo address',
            }
            collection = utils.makeOneCollection(attrib=collection_data)
            # when
            response = self.client.get(url_for('main.about_collection'))
            # then
            self.assertStatus(response, 200)
            self.assertIn(collection['address1'], response.data.decode('utf-8'))
            self.assertIn(collection['address2'], response.data.decode('utf-8'))

    def test_collection_address_at_journal_list_page_footer(self):
        """
        acessar na pagina Alfabética deve mostrar o endereço da coleção
        """
        # with
        with current_app.app_context():
            collection_data = {
                'address1': 'foo address',
                'address2': 'foo address',
            }
            collection = utils.makeOneCollection(attrib=collection_data)
            # when
            response = self.client.get(url_for('main.collection_list'))
            # then
            self.assertStatus(response, 200)
            self.assertIn(collection['address1'], response.data.decode('utf-8'))
            self.assertIn(collection['address2'], response.data.decode('utf-8'))

    def test_home_page_last_issues(self):
        """
        Teste da página inicial, deve retorna utf-8 como conjunto de caracter e
        o template ``collection/index.html``.
        """
        with current_app.app_context():

            utils.makeOneCollection()
            issues = [
                {'volume': '2', 'number': '5B', 'year': '2011'},
                {'volume': '12', 'suppl_text': 'suppl', 'year': '2015'},
                {'volume': '23', 'year': '2016'},
                {'number': '43', 'year': '2017'},
            ]
            journals = utils.makeAnyJournal(items=len(issues))
            for journal, _issue in zip(journals, issues):
                _issue.update({'journal': journal})
                journal.last_issue = utils.makeOneIssue(_issue)

            for journal, expected_issue in zip(journals, issues):
                context = {
                    'journal': journal
                }
                response_data = render_template(
                                    "news/includes/issue_last_row.html",
                                    **context)
                self.assertIn(
                    'Ano: </strong><b>{}'.format(
                        expected_issue.get('year')),
                    response_data)

                fields = ['volume', 'number', 'suppl_text']
                labels = ['Volume', 'Número', 'Suplemento']
                for label, field in zip(labels, fields):
                    value = expected_issue.get(field)
                    if value is None:
                        assert_function = self.assertNotIn
                    else:
                        assert_function = self.assertIn
                    assert_function(
                        '{}: </strong><b>{}'.format(label, value),
                        response_data)

    def test_get_robots_txt_file(self):
        """
        Teste de acesso ao arquivo robots.txt.
        """
        with current_app.app_context():
            utils.makeOneCollection()
            with self.client as c:
                response = c.get('/robots.txt')
                self.assertStatus(response, 200)
                self.assertIn('User-agent: *', response.data.decode('utf-8'))
                self.assertIn('Disallow: /', response.data.decode('utf-8'))


class PageTestCase(BaseTestCase):

    def test_pages_list(self):
        """
        Teste para avaliar o retorno da ``view function`` pages,
        ao cadastrar 3 páginas a interface deve retornar uma listagem
        contendo elementos esperados e também deve retornar o template
        ``collection/about.html``.
        """
        utils.makeOneCollection()
        pages = [
            utils.makeOnePage({'name': 'Criterios SciELO',
                               'language': 'es_ES'}),
            utils.makeOnePage({'name': 'Critérios SciELO',
                               'language': 'pt_BR'}),
            utils.makeOnePage({'name': 'FAQ SciELO',
                               'language': 'pt_BR'}),
            utils.makeOnePage({'name': 'Equipe SciELO',
                               'language': 'pt_BR'})
        ]

        response = self.client.get(url_for('main.about_collection'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/about.html')

        for page in pages:
            if page.language == 'pt_BR':
                self.assertIn(
                    '/about/%s' % (page.slug_name),
                    response.data.decode('utf-8'))

        self.assertListEqual(
            sorted([page.slug_name for page in pages[1:]]),
            sorted(
                [page.slug_name
                 for page in self.get_context_variable('pages')]))

    def test_page(self):
        """
        Teste da ``view function`` ``page``, deve retornar uma página
        que usa o template ``collection/about.html``.
        """
        with current_app.app_context():
            utils.makeOneCollection()

            page = utils.makeOnePage({'name': 'Critérios SciELO',
                                      'language': 'pt_BR'})
            response = self.client.get(url_for('main.about_collection',
                                               slug_name=page.slug_name))

            self.assertEqual(200, response.status_code)
            self.assertTemplateUsed('collection/about.html')
            self.assertIn('Critérios SciELO', response.data.decode('utf-8'))
            self.assertIn('"/about/"', response.data.decode('utf-8'))
            self.assertEqual(
                self.get_context_variable('page').slug_name, page.slug_name)

    def test_page_with_unknown_name(self):
        """
        Teste da ``view function`` ``page`` com um id desconhecido
        deve retornar uma página com ``status_code`` 404 e msg
        ``Página não encontrada``.
        """
        with current_app.app_context():
            utils.makeOneCollection()
            unknown_page_name = 'xxjfsfadfa0k2qhs8slwnui8'
            response = self.client.get(url_for('main.about_collection',
                                       slug_name=unknown_page_name))
            self.assertStatus(response, 404)


    def test_page_when_is_draft_collection(self):
        """
        Teste da ``view function`` ``page``, deve retornar uma página
        que usa o template ``collection/about.html`` quando está em rascunho.

        """
        with current_app.app_context():
            utils.makeOneCollection()

            page = utils.makeOnePage({'name': 'Critérios SciELO',
                                      'language': 'pt_BR',
                                      'is_draft': True})
            response = self.client.get(url_for('main.about_collection',
                                               slug_name=page.slug_name))

            self.assertEqual(404, response.status_code)
            self.assertIn('Página não encontrada', response.data.decode('utf-8'))


    def test_page_when_is_draft_journal(self):
        """
        Teste da ``view function`` ``page``, deve retornar uma página
        que usa o template ``journal/about.html``, retorna que o
        ``Conteúdo não cadastrado.``
        """
        with current_app.app_context():
            utils.makeOneCollection()

            page = utils.makeOnePage({'name': 'Critérios SciELO',
                                      'language': 'pt_BR',
                                      'is_draft': True})
            response = self.client.get(url_for('main.about_journal',
                                               url_seg=page.slug_name))

            self.assertEqual(404, response.status_code)


class TestJournaDetail(BaseTestCase):

        # JOURNAL

    def test_journal_detail(self):
        """
        Teste da ``view function`` ``journal_detail``, deve retornar uma página
        que usa o template ``journal/detail.html`` e o título do periódico no
        corpo da página.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal({'title': 'Revista X'})

            response = self.client.get(url_for('main.journal_detail',
                                               url_seg=journal.url_segment))

            self.assertTrue(200, response.status_code)
            self.assertTemplateUsed('journal/detail.html')
            self.assertIn('Revista X',
                          response.data.decode('utf-8'))
            self.assertEqual(self.get_context_variable('journal').id, journal.id)

    def test_journal_detail_legacy_url(self):
        """
        Teste da ``view function`` ``journal_detail_legacy_url``, deve retorna status_code 301
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal({'title': 'Revista X'})

            response = self.client.get("/journal/acron")

            self.assertTrue(301, response.status_code)

    def test_journal_detail_url_journal_acron(self):
        """
        Teste da ``view function`` ``journal_detail_url_journal_acron``, deve retorna status_code 301
        """
        with current_app.app_context():
            utils.makeOneCollection()
            journal = utils.makeOneJournal({'title': 'Revista X'})
            response = self.client.get("/acron")
            self.assertTrue(301, response.status_code)

    def test_journal_detail_legacy_url_follow_redirect(self):
        """
        Teste da ``view function`` ``journal_detail_legacy_url``, deve retornar uma página
        que usa o template ``journal/detail.html`` e o título do periódico no
        corpo da página.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal({'title': 'Revista X'})

            response = self.client.get(
                                    url_for(
                                       'main.journal_detail_legacy_url', journal_seg=journal.url_segment),
                                    follow_redirects=True)

            self.assertTrue(200, response.status_code)
            self.assertTemplateUsed('journal/detail.html')
            self.assertIn('Revista X',
                          response.data.decode('utf-8'))
            self.assertEqual(self.get_context_variable('journal').id, journal.id)

    def test_journal_detail_with_unknow_id(self):
        """
        Teste da ``view function`` ``journal_detail`` com um id desconhecido
        deve retornar uma página com ``status_code`` 404 e msg
        ``Periódico não encontrado``.
        """

        utils.makeAnyJournal(items=6)

        unknow_url_seg = '0k2qhs8slwnui8'

        response = self.client.get(url_for('main.journal_detail',
                                   url_seg=unknow_url_seg))

        self.assertStatus(response, 404)
        self.assertIn('Periódico não encontrado',
                      response.data.decode('utf-8'))

    def test_journal_detail_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``journal_detail`` acessando um periódico
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """
        unpublish_reason = 'plágio'
        journal = utils.makeOneJournal({
            'is_public': False,
            'unpublish_reason': unpublish_reason})

        response = self.client.get(url_for('main.journal_detail',
                                           url_seg=journal.url_segment))

        self.assertStatus(response, 404)
        self.assertIn(unpublish_reason, response.data.decode('utf-8'))


class TestJournalGrid(BaseTestCase):

    def test_issue_grid(self):
        """
        Teste da ``view function`` ``issue_grid`` acessando a grade de números
        de um periódico, nesse teste deve ser retornado todos os números com
        o atributo is_public=True de um número, sendo que o template deve ser
        ``issue/grid.html``.
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issues = utils.makeAnyIssue(attrib={'journal': journal.id})

            response = self.client.get(url_for('main.issue_grid',
                                       url_seg=journal.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/grid.html')

            for issue in issues:
                self.assertIn('/journal_acron', response.data.decode('utf-8'))

    def test_issue_grid_without_issues(self):
        """
        Teste para avaliar o retorno da ``view function`` ``issue_grid``
        quando não existe número cadastrado deve retornar ``status_code`` 200
        e a msg ``Nenhum número encontrado para esse perióico``
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            response = self.client.get(
                url_for('main.issue_grid', url_seg=journal.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/grid.html')

            self.assertIn('Nenhum número encontrado para esse periódico',
                          response.data.decode('utf-8'))

    def test_issue_grid_with_unknow_journal_id(self):
        """
        Teste para avaliar o retorno da ``view function`` ``issue_grid``
        quando é acessado utilizando um identificador do periódico desconhecido,
        deve retornar status_code 404 com a msg ```Periódico não encontrado``.
        """

        journal = utils.makeOneJournal()

        utils.makeAnyIssue(attrib={'journal': journal.id})

        unknow_url_seg = '9km2g78o2mnu7'

        response = self.client.get(
            url_for('main.issue_grid', url_seg=unknow_url_seg))

        self.assertStatus(response, 404)

        self.assertIn('Periódico não encontrado',
                      response.data.decode('utf-8'))

    def test_issue_grid_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_grid`` acessando um periódico
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """
        unpublish_reason = 'Problema de Direito Autoral'
        journal = utils.makeOneJournal({'is_public': False,
                                       'unpublish_reason': unpublish_reason})

        response = self.client.get(url_for('main.issue_grid',
                                           url_seg=journal.url_segment))

        self.assertStatus(response, 404)
        self.assertIn(unpublish_reason, response.data.decode('utf-8'))

    def test_issue_grid_legacy_redirects(self):
        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issues = utils.makeAnyIssue(attrib={'journal': journal.id})

            response = self.client.get('/grid/{}'.format(journal.url_segment))

            self.assertStatus(response, 301)

    def test_issue_grid_social_meta_tags(self):
        """
        Teste para verificar a página da grade do periódico apresenta as
        tags de compartilhamento com redes sociais.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal({'title': 'Social Meta tags'})

            response = self.client.get(
                url_for('main.issue_grid', url_seg=journal.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/grid.html')
            self.assertIn('<meta property="og:url" content="http://0.0.0.0:8000/j/journal_acron/grid" />', response.data.decode('utf-8'))
            self.assertIn('<meta property="og:type" content="website" />', response.data.decode('utf-8'))
            self.assertIn('<meta property="og:title" content="Social Meta tags" />', response.data.decode('utf-8'))
            self.assertIn('<meta property="og:description" content="Esse periódico tem com objetivo xpto" />', response.data.decode('utf-8'))
            self.assertIn('<meta property="og:image" content="http://0.0.0.0:8000/None" />', response.data.decode('utf-8'))


class TestIssueToc(BaseTestCase):

    def test_issue_toc(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando a página do número,
        deve retorna status_code 200 e o template ``issue/toc.html``.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'number': '31',
                                        'volume': '10',
                                        'journal': journal})

            response = self.client.get(url_for('main.issue_toc',
                                       url_seg=journal.url_segment,
                                       url_seg_issue=issue.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/toc.html')
            # self.assertIn(u'Vol. 10 No. 31', response.data.decode('utf-8'))
            self.assertEqual(self.get_context_variable('issue').id, issue.id)

    def test_issue_toc_unknow_issue_id(self):
        """
        Teste para avaliar o retorno da ``view function`` ``issue_toc``
        quando é acessado utilizando um identificador do issue desconhecido,
        deve retorna status_code 404 com a msg ``Número não encontrado``.
        """
        journal = utils.makeOneJournal()

        utils.makeOneIssue({'journal': journal})

        unknow_url_seg = '2014.v3n2'

        unknow_url = url_for(
            'main.issue_toc',
            url_seg=journal.url_segment,
            url_seg_issue=unknow_url_seg)

        response = self.client.get(unknow_url)

        self.assertStatus(response, 404)
        self.assertIn('Número não encontrado', response.data.decode('utf-8'))

    def test_issue_toc_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando um número
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """
        unpublish_reason = 'Número incorreto'
        journal = utils.makeOneJournal()
        issue = utils.makeOneIssue({
            'is_public': False,
            'unpublish_reason': unpublish_reason,
            'journal': journal})

        response = self.client.get(url_for('main.issue_toc',
                                           url_seg=journal.url_segment,
                                           url_seg_issue=issue.url_segment))

        self.assertStatus(response, 404)
        self.assertIn(unpublish_reason, response.data.decode('utf-8'))

    def test_issue_toc_with_journal_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando um número
        com atributo is_public=True, porém com um periódico com atributo
        is_public=False deve retorna uma página com ``status_code`` 404 e msg
        cadastrada no atributo ``reason`` do periódico.
        """
        unpublish_reason = 'Revista removida da coleção'
        journal = utils.makeOneJournal({
            'is_public': False,
            'unpublish_reason': unpublish_reason})
        issue = utils.makeOneIssue({
            'is_public': True,
            'journal': journal.id})

        response = self.client.get(url_for('main.issue_toc',
                                           url_seg=journal.url_segment,
                                           url_seg_issue=issue.url_segment))

        self.assertStatus(response, 404)
        self.assertIn(unpublish_reason, response.data.decode('utf-8'))

    def test_issue_toc_legacy_redirects_to_issue_toc(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando a página do número,
        deve retorna status_code 200 e o template ``issue/toc.html``.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'number': '31',
                                        'volume': '10',
                                        'journal': journal})

            response = self.client.get(url_for('main.issue_toc_legacy',
                                       url_seg=journal.url_segment,
                                       url_seg_issue=issue.url_segment))

            self.assertStatus(response, 301)

    def test_issue_toc_legacy_redirects_to_aop_toc(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando a página do número,
        deve retorna status_code 200 e o template ``issue/toc.html``.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'number': 'ahead',
                                        'type': 'ahead',
                                        'journal': journal})

            response = self.client.get(url_for('main.issue_toc_legacy',
                                       url_seg=journal.url_segment,
                                       url_seg_issue=issue.url_segment))

            self.assertStatus(response, 301)
            self.assertRedirects(
                response,
                url_for(
                    'main.aop_toc',
                    url_seg=journal.url_segment
                ),
            )

    def test_issue_toc_redirects_to_aop_toc(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando a página do número,
        deve retorna status_code 200 e o template ``issue/toc.html``.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'number': 'ahead',
                                        'type': 'ahead',
                                        'journal': journal})

            response = self.client.get(url_for('main.issue_toc',
                                       url_seg=journal.url_segment,
                                       url_seg_issue=issue.url_segment))

            self.assertStatus(response, 301)
            self.assertRedirects(
                response,
                url_for(
                    'main.aop_toc',
                    url_seg=journal.url_segment
                ),
            )

    def test_issue_toc_social_meta_tags(self):
        """
        Teste para verificar a página da TOC do periódico apresenta as
        tags de compartilhamento com redes sociais.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal({'title': 'Social Meta tags'})

            issue = utils.makeOneIssue({'number': '31',
                                        'volume': '10',
                                        'journal': journal})

            response = self.client.get(url_for('main.issue_toc',
                                       url_seg=journal.url_segment,
                                       url_seg_issue=issue.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/toc.html')

            self.assertIn(
                '<meta property="og:url" content="http://0.0.0.0:8000/j/journal_acron/i/2021.v10n31supplX/" />', response.data.decode('utf-8'))
            self.assertIn('<meta property="og:type" content="website" />', response.data.decode('utf-8'))
            self.assertIn('<meta property="og:title" content="Social Meta tags" />', response.data.decode('utf-8'))
            self.assertIn('<meta property="og:description" content="Esse periódico tem com objetivo xpto" />', response.data.decode('utf-8'))
            self.assertIn('<meta property="og:image" content="http://0.0.0.0:8000/None" />', response.data.decode('utf-8'))


class TestAOPToc(BaseTestCase):

    def test_aop_toc_returns_one_aop_with_one_article(self):
        """
        Teste da ``view function`` ``aop_toc`` acessando a página do número,
        deve retornar status_code 200 e o template ``issue/toc.html``.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue(
                {
                    'number': 'ahead',
                    'journal': journal,
                    'type': 'ahead',
                }
            )
            article = utils.makeOneArticle(
                {
                    'title': 'Article Y',
                    'original_language': 'en',
                    'languages': ['es', 'pt'],
                    'translated_titles': [
                        {'language': 'es', 'name': u'Artículo en español'},
                        {'language': 'pt', 'name': u'Artigo en Português'},
                    ],
                    'issue': issue,
                    'journal': journal,
                    'url_segment': 'ahead'
                }
            )

            url = url_for('main.aop_toc', url_seg=journal.url_segment)
            response = self.client.get(url)

            self.assertStatus(response, 200)
            self.assertEqual(
                len(self.get_context_variable('articles')),
                1
            )
            self.assertTemplateUsed('issue/toc.html')

    def test_aop_toc_returns_not_found_because_of_there_is_no_aop(self):
        """
        Teste da ``view function`` ``aop_toc`` acessando a página do número,
        deve retornar status_code 404.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            url = url_for('main.aop_toc', url_seg=journal.url_segment)
            response = self.client.get(url)
            self.assertStatus(response, 404)

    def test_aop_toc_returns_not_found_because_of_not_published_articles(self):
        """
        Teste da ``view function`` ``aop_toc`` acessando a página do número,
        deve retornar status_code 404.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue(
                {
                    'number': 'ahead',
                    'journal': journal,
                    'type': 'ahead',
                }
            )
            article = utils.makeOneArticle(
                {
                    'issue': issue,
                    'journal': journal,
                    'is_public': False,
                }
            )

            url = url_for('main.aop_toc', url_seg=journal.url_segment)
            response = self.client.get(url)
            self.assertStatus(response, 404)

    def test_aop_toc_returns_not_found_because_of_not_published_aop(self):
        """
        Teste da ``view function`` ``aop_toc`` acessando a página do número,
        deve retornar status_code 404.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue(
                {
                    'number': 'ahead',
                    'journal': journal,
                    'type': 'ahead',
                    'is_public': False,
                }
            )

            url = url_for('main.aop_toc', url_seg=journal.url_segment)
            response = self.client.get(url)
            self.assertStatus(response, 404)

    def test_aop_toc_returns_not_found_because_of_aop_has_no_article(self):
        """
        Teste da ``view function`` ``aop_toc`` acessando a página do número,
        deve retornar status_code 404.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue(
                {
                    'number': 'ahead',
                    'journal': journal,
                    'type': 'ahead',
                }
            )

            url = url_for('main.aop_toc', url_seg=journal.url_segment)
            response = self.client.get(url)
            self.assertStatus(response, 404)

    def test_aop_toc_returns_not_found_because_of_journal_is_not_public(self):
        """
        Teste da ``view function`` ``aop_toc`` acessando a página do número,
        deve retornar status_code 404.
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal({'is_public': False})

            issue = utils.makeOneIssue(
                {
                    'number': 'ahead',
                    'journal': journal,
                    'type': 'ahead',
                }
            )

            url = url_for('main.aop_toc', url_seg=journal.url_segment)
            response = self.client.get(url)
            self.assertStatus(response, 404)


class TestArticleDetailV3Meta(BaseTestCase):

    def test_article_detail_v3_creates_meta_citation_pdf_url_only_for_the_selected_lang(self):
        """
        Teste se ``view function`` ``article_detail_v3``,
        cria a tag meta cujo name="citation_pdf_url" e conteúdo do endereço do
        pdf no padrão
        https://website/j/acron/a/pidv3/?format=pdf&amp;lang=idioma_selecionado
        `<meta name="citation_pdf_url"
          content="https://website/j/acron/a/pidv3/?format=pdf&amp;lang=idioma_selecionado"/>`

        Verifica na view se o valor da variável FORCE_USE_HTTPS_GOOGLE_TAGS é True ou False,
        no caso de True monta a URL para o PDF sempre com protocolo https, em caso de False
        monta a URL com o ``scheme`` obtido pelo urlparsed.scheme.

        FORCE_USE_HTTPS_GOOGLE_TAGS is False in testting.template
        """

        with current_app.test_request_context() as context:
            utils.makeOneCollection()
            journal = utils.makeOneJournal()
            issue = utils.makeOneIssue({'journal': journal})
            article = utils.makeOneArticle({
                'title': 'Article Y',
                'original_language': 'en',
                'languages': ['es', 'pt', 'en'],
                'pdfs': [{
                    'lang': 'en',
                    'url': 'http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651aen.pdf',
                    'file_path': '/pdf/cta/v39s2/0101-2061-cta-fst30618-en.pdf',
                    'type': 'pdf'
                },
                {
                    'lang': 'pt',
                    'url': 'http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651apt.pdf',
                    'file_path': '/pdf/cta/v39s2/0101-2061-cta-fst30618-pt.pdf',
                    'type': 'pdf'
                },
                {
                    'lang': 'es',
                    'url': 'http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651aes.pdf',
                    'file_path': '/pdf/cta/v39s2/0101-2061-cta-fst30618-es.pdf',
                    'type': 'pdf'
                }
                ],
                'issue': issue,
                'journal': journal,
                'url_segment': '10-11'
            })

            response = self.client.get(
                url_for(
                    'main.article_detail_v3',
                    url_seg=journal.url_segment,
                    article_pid_v3=article.aid,
                    lang="es"
                )
            )
            self.assertStatus(response, 200)
            content = response.data.decode('utf-8')

            soup = BeautifulSoup(content, 'html.parser')
            meta_tags = soup.find_all(attrs={"name": "citation_pdf_url"})
            self.assertEqual(len(meta_tags), 1)

            content_url = urlparse(meta_tags[0].get("content"))
            self.assertEqual(
                "{}://{}/".format(content_url.scheme,
                                  content_url.netloc),
                context.request.url_root
            )
            self.assertEqual(
                content_url.path, "/j/journal_acron/a/{}/".format(article.aid)
            )
            self.assertEqual(
                parse_qs(content_url.query), {'format': ['pdf'], 'lang': ['es']}
            )

    def test_article_detail_v3_creates_meta_citation_xml_url(self):
        """
        Teste se ``view function`` ``article_detail_v3``,
        cria a tag meta cujo name="citation_xml_url" e conteúdo do endereço do
        pdf no padrão
        https://website/j/acron/a/pidv3/?format=xml
        `<meta name="citation_xml_url"
          content="https://website/j/acron/a/pidv3/?format=xml"/>`

        Verifica na view se o valor da variável FORCE_USE_HTTPS_GOOGLE_TAGS é True ou False,
        no caso de True monta a URL para o XML sempre com protocolo https, em caso de False
        monta a URL com o ``scheme`` obtido pelo urlparsed.scheme.

        FORCE_USE_HTTPS_GOOGLE_TAGS is False in testting.template
        """

        with current_app.test_request_context() as context:
            utils.makeOneCollection()
            journal = utils.makeOneJournal()
            issue = utils.makeOneIssue({'journal': journal})
            article = utils.makeOneArticle({
                'title': 'Article Y',
                'original_language': 'en',
                'languages': ['es', 'pt', 'en'],
                'issue': issue,
                'journal': journal,
                'url_segment': '10-11'
            })

            response = self.client.get(
                url_for(
                    'main.article_detail_v3',
                    url_seg=journal.url_segment,
                    article_pid_v3=article.aid,
                )
            )

            self.assertStatus(response, 200)
            content = response.data.decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            meta_tags = soup.find_all(attrs={"name": "citation_xml_url"})
            self.assertEqual(len(meta_tags), 1)

            content_url = urlparse(meta_tags[0].get("content"))
            self.assertEqual(
                "{}://{}/".format(content_url.scheme, content_url.netloc),
                context.request.url_root
            )
            self.assertEqual(
                content_url.path, "/j/journal_acron/a/{}/".format(article.aid)
            )
            self.assertEqual(
                parse_qs(content_url.query), {'format': ['xml'], 'lang': ['en']}
            )

    def test_article_detail_v3_social_meta_tags(self):
        """
        Teste para verificar a página do artigo apresenta as tags de compartilhamento
        com redes sociais.
        """

        with current_app.test_request_context() as context:
            utils.makeOneCollection({ 'acronym': "DUMMY_TEST2" })
            journal = utils.makeOneJournal()
            issue = utils.makeOneIssue({'journal': journal})
            article = utils.makeOneArticle({
                'title': 'Article Y',
                'original_language': 'en',
                'languages': ['es', 'pt', 'en'],
                'issue': issue,
                'journal': journal,
                'url_segment': '10-11'
            })

            response = self.client.get(
                url_for(
                    'main.article_detail_v3',
                    url_seg=journal.url_segment,
                    article_pid_v3=article.aid,
                )
            )

            self.assertStatus(response, 200)
            content = response.data.decode('utf-8')

            self.assertIn(
                '<meta property="og:url" content="http://0.0.0.0:8000/j/journal_acron/a/%s/"/>' % article.aid, response.data.decode('utf-8'))
            self.assertIn('<meta property="og:type" content="article"/>', response.data.decode('utf-8'))
            self.assertIn('<meta property="og:title" content="%s"/>' % article.title, response.data.decode('utf-8'))
            self.assertIn('<meta property="og:description" content="%s"/>' % article.abstract, response.data.decode('utf-8'))
            self.assertIn('<meta property="og:image" content="http://0.0.0.0:8000/None"/>', response.data.decode('utf-8'))

    def test_article_detail_v3_citation_author_tags(self):
        """
        Teste para verificar a página do artigo apresenta as tags author com
        afiliação e ORCID.
        """

        with current_app.test_request_context() as context:
            utils.makeOneCollection({ 'acronym': "DUMMY_TEST2" })
            journal = utils.makeOneJournal()
            issue = utils.makeOneIssue({'journal': journal})
            article = utils.makeOneArticle({
                'title': 'Article Y',
                'original_language': 'en',
                'languages': ['es', 'pt', 'en'],
                'issue': issue,
                'journal': journal,
                'url_segment': '10-11',
                'authors_meta': [
                                    {
                                        "name" : "Arias, Sarah Muñoz",
                                        "affiliation" : "Universidad Tecnológica de Pereira",
                                        "orcid" : "0000-0002-3430-5422"
                                    },
                                    {
                                        "name" : "Álvarez, Gloria Edith Guerrero",
                                        "affiliation" : "Universidad Tecnológica de Pereira",
                                        "orcid" : "0000-0002-0529-5835"
                                    },
                                    {
                                        "name" : "Patiño, Paula Andrea González",
                                        "affiliation" : "Universidad Tecnológica de Pereira",
                                        "orcid" : "0000-0002-7323-9261"
                                    }
                                ]
                })

            response = self.client.get(
                url_for(
                    'main.article_detail_v3',
                    url_seg=journal.url_segment,
                    article_pid_v3=article.aid,
                )
            )

            self.assertStatus(response, 200)
            content = response.data.decode('utf-8')

            self.assertIn(
                '<meta name="citation_author" content="Arias, Sarah Muñoz">', content)
            self.assertIn('<meta name="citation_author_affiliation" content="Universidad Tecnológica de Pereira">', content)
            self.assertIn('<meta name="citation_author_orcid" content="http://orcid.org/0000-0002-3430-5422">', content)
            self.assertIn('<meta name="citation_author" content="Álvarez, Gloria Edith Guerrero">', content)
            self.assertIn('<meta name="citation_author_affiliation" content="Universidad Tecnológica de Pereira">', content)
            self.assertIn('<meta name="citation_author_orcid" content="http://orcid.org/0000-0002-0529-5835">', content)
            self.assertIn('<meta name="citation_author" content="Patiño, Paula Andrea González">', content)
            self.assertIn('<meta name="citation_author_affiliation" content="Universidad Tecnológica de Pereira">', content)
            self.assertIn('<meta name="citation_author_orcid" content="http://orcid.org/0000-0002-7323-9261">', content)
