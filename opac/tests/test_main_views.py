# coding: utf-8
import unittest
import flask
import warnings
from flask_testing import TestCase
from flask import url_for, request, g, current_app
from webapp import create_app, dbsql, dbmongo

from base import MongoInstance, BaseTestCase

from opac_schema.v1 import models

import utils
from base import BaseTestCase


class MainTestCase(BaseTestCase):

    def test_home_page(self):
        """
        Teste da página inicial, deve retorna utf-8 como conjunto de caracter e
        o template ``collection/index.html``.
        """
        with self.client as c:
            response = c.get(url_for('main.index'))
            self.assertStatus(response, 200)
            self.assertEqual('text/html; charset=utf-8', response.content_type)
            self.assert_template_used("collection/index.html")

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
                response = self.client.get(url_for('main.index'))
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
            response = c.get(url_for('main.set_locale', lang_code='es_ES'))
            self.assertEqual(302, response.status_code)
            self.assertEqual(flask.session['lang'], 'es_ES')

    def test_redirect_when_change_set_locale(self):
        """
        Teste para verificar se o redirecionamento da ``view function``
        ``set_locale`` retorna para a página esperada.
        """

        with self.client as c:
            response = c.get(url_for('main.set_locale', lang_code='es_ES'),
                             headers={'Referer': '/journals'},
                             follow_redirects=True)
            self.assertStatus(response, 200)

            self.assertTemplateUsed('collection/list_alpha.html')

    def test_change_set_locale_with_unknow_lang(self):
        """
        Teste para alterar o idioma da interface, nesse teste a URL:
        '/set_locale/<string:lang_code>' deve retornar uma página com
        ``status_code``400 e manter o idioma padrão ``pt_BR``.
        """
        expected_message = u'<p>Código de idioma inválido</p>'

        with self.client as c:
            response = c.get(url_for('main.set_locale', lang_code='en_US'))
            self.assertEqual(400, response.status_code)
            self.assertIn(u'Código de idioma inválido',
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
        collecton = utils.makeOneCollection()
        journals = utils.makeAnyJournal(items=10)

        response = self.client.get(url_for('main.collection_list_alpha'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_alpha.html')

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

        collecton = utils.makeOneCollection()
        response = self.client.get(url_for('main.collection_list_alpha'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_alpha.html')

        self.assertIn(u'Nenhum periódico encontrado',
                      response.data.decode('utf-8'))

    @unittest.skip("Revisar/Refazer, agora a lista é carregada com ajax")
    def test_collection_list_theme(self):
        """
        Teste para avaliar o retorno da ``view function`` collection_list_theme
        ao cadastrarmos 60 periódico a interface deve retornar uma listagem
        contendo elementos esperado tambémdeve retornar o template
        ``collection/list_theme.html``.
        """

        collecton = utils.makeOneCollection()
        journals = utils.makeAnyJournal(items=30,
                                        attrib={"study_areas": ["Engineering"]})
        journals = utils.makeAnyJournal(items=30,
                                        attrib={"study_areas": ["Human Sciences",
                                                "Biological Sciences", "Engineering"]})

        response = self.client.get(url_for('main.collection_list_theme'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_theme.html')

        for journal in journals:
            self.assertIn('journals/%s' % journal.id,
                          response.data.decode('utf-8'))

    def test_collection_list_theme_without_journals(self):
        """
        Teste para avaliar o retorno da ``view function`` collection_list_theme
        quando não existe periódicos cadastrados deve retorna a msg
        ``Nenhum periódico encontrado`` no corpo da resposta.
        """

        collecton = utils.makeOneCollection()
        response = self.client.get(url_for('main.collection_list_theme'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_theme.html')

        self.assertIn(u'Nenhum periódico encontrado',
                      response.data.decode('utf-8'))

    @unittest.skip("Revisar/Refazer, agora a lista é carregada com ajax")
    def test_collection_list_institution(self):
        """
        Teste para a ``view function`` collection_list_institution, será avaliado
        somente o template utilizado pois essa função depende de definição do atributo
        instituição no manager.
        """

        collecton = utils.makeOneCollection()
        warnings.warn("Necessário definir o atributo instituição no modelo do Manager")

        response = self.client.get(url_for('main.collection_list_institution'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_institution.html')

    def test_collection_list_institution_without_journals(self):
        """
        Teste para avaliar o retorno da ``view function`` collection_list_institution
        quando não existe periódicos cadastrados deve retorna a msg
        ``Nenhum periódico encontrado`` no corpo da resposta.
        """

        collecton = utils.makeOneCollection()
        response = self.client.get(url_for('main.collection_list_institution'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_institution.html')

        self.assertIn(u'Nenhum periódico encontrado',
                      response.data.decode('utf-8'))

    def test_collection_list_feed(self):
        """
        Teste para verificar a reposta da ``view funciton``collection_list_feed
        Se cadastra 10 periódicos, deve retornar na interface do rss, utilizando
        o template ``collection/list_feed_content.html```.
        """

        with current_app.app_context():

            collection = utils.makeOneCollection()
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
                self.assertIn('journals/%s' % journal.id,
                              response.data.decode('utf-8'))

            for issue in issues:
                self.assertIn('issues/%s' % issue.id,
                              response.data.decode('utf-8'))

    def test_collection_list_feed_without_journals(self):
        """
        Teste para avaliar o retorno da ``view function`` collection_list_feed
        quando não existe periódicos cadastrados deve retorna a msg
        ``Nenhum periódico encontrado`` no corpo da resposta.
        """
        with current_app.app_context():

            collection = utils.makeOneCollection()

            response = self.client.get(url_for('main.collection_list_feed'))

            self.assertStatus(response, 200)
            self.assertIn(u'Nenhum periódico encontrado',
                          response.data.decode('utf-8'))

    def test_collection_list_feed_without_issues(self):
        """
        Teste para verificar a reposta da ``view funciton``collection_list_feed
        Se cadastra 10 periódicos sem fascículo, deve retornar na interface do
        rss, utilizando o template ``collection/list_feed_content.html```.
        """

        with current_app.app_context():

            collection = utils.makeOneCollection()
            journals = utils.makeAnyJournal(items=10)

            response = self.client.get(url_for('main.collection_list_feed'))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('collection/list_feed_content.html')

            for journal in journals:
                self.assertIn('journals/%s' % journal.id,
                              response.data.decode('utf-8'))

    # JOURNAL

    def test_journal_detail(self):
        """
        Teste da ``view function`` ``journal_detail``, deve retornar uma página
        que usa o template ``journal/detail.html`` e o título do periódico no
        corpo da página.
        """

        with current_app.app_context():

            collection = utils.makeOneCollection()

            journal = utils.makeOneJournal({'title': 'Revista X'})

            response = self.client.get(url_for('main.journal_detail',
                                               journal_id=journal.id))

            self.assertTrue(200, response.status_code)
            self.assertTemplateUsed('journal/detail.html')
            self.assertIn(u'Revista X',
                          response.data.decode('utf-8'))
            self.assertEqual(self.get_context_variable('journal').id, journal.id)

    def test_journal_detail_with_unknow_id(self):
        """
        Teste da ``view function`` ``journal_detail`` com um id desconhecido
        deve retornar uma página com ``status_code`` 404 e msg
        ``Periódico não encontrado``.
        """

        journals = utils.makeAnyJournal(items=6)

        unknow_id = '0k2qhs8slwnui8'

        response = self.client.get(url_for('main.journal_detail',
                                   journal_id=unknow_id))

        self.assertStatus(response, 404)
        self.assertIn(u'Periódico não encontrado',
                      response.data.decode('utf-8'))

    def test_journal_detail_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``journal_detail`` acessando um periódico
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """

        journal = utils.makeOneJournal({
            'is_public': False,
            'unpublish_reason': 'plágio'})

        response = self.client.get(url_for('main.journal_detail',
                                           journal_id=journal.id))

        self.assertStatus(response, 404)
        self.assertIn(u'plágio', response.data.decode('utf-8'))

    def test_journal_feed(self):
        """
        Teste da ``view function`` ``journal_feed``, deve retornar um rss
        que usa o template ``issue/feed_content.html`` e o título do periódico no
        corpo da página.
        """

        with current_app.app_context():
            collection = utils.makeOneCollection()
            journal = utils.makeOneJournal({'title': 'Revista X'})
            issue = utils.makeOneIssue({'journal': journal})
            articles = utils.makeAnyArticle(
                issue=issue,
                attrib={'journal': journal.id, 'issue': issue.id}
            )

            response = self.client.get(url_for('main.journal_feed',
                                               journal_id=journal.id))

            self.assertTrue(200, response.status_code)
            self.assertTemplateUsed('issue/feed_content.html')

    def test_journal_feed_with_unknow_id(self):
        """
        Teste da ``view function`` ``journal_feed`` com um id desconhecido
        deve retornar uma página com ``status_code`` 404 e msg
        ``Periódico não encontrado``.
        """

        journals = utils.makeAnyJournal(items=6)

        unknow_id = '0k2qhs8slwnui8'

        response = self.client.get(url_for('main.journal_feed',
                                   journal_id=unknow_id))

        self.assertStatus(response, 404)
        self.assertIn(u'Periódico não encontrado',
                      response.data.decode('utf-8'))

    def test_journal_feed_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``journal_feed`` acessando um periódico
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """

        journal = utils.makeOneJournal({
            'is_public': False,
            'unpublish_reason': 'plágio'})

        response = self.client.get(url_for('main.journal_feed',
                                           journal_id=journal.id))

        self.assertStatus(response, 404)
        self.assertIn(u'plágio', response.data.decode('utf-8'))

    # ISSUE

    def test_issue_grid(self):
        """
        Teste da ``view function`` ``issue_grid`` acessando a grade de fascículos
        de um periódico, nesse teste deve ser retornado todos os fascículos com
        o atributo is_public=True de um fascículo, sendo que o template deve ser
        ``issue/grid.html``.
        """

        with current_app.app_context():
            collection = utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issues = utils.makeAnyIssue(attrib={'journal': journal.id})

            response = self.client.get(url_for('main.issue_grid',
                                       journal_id=journal.id))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/grid.html')

            for issue in issues:
                self.assertIn('/issues/%s' % issue.id, response.data.decode('utf-8'))

    def test_issue_grid_without_issues(self):
        """
        Teste para avaliar o retorno da ``view function`` ``issue_grid``
        quando não existe fascículo cadastrado deve retornar ``status_code`` 200
        e a msg ``Nenhum fascículo encontrado para esse perióico``
        """

        with current_app.app_context():

            collection = utils.makeOneCollection()

            journal = utils.makeOneJournal()

            response = self.client.get(url_for('main.issue_grid',
                                       journal_id=journal.id))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/grid.html')

            self.assertIn(u'Nenhum fascículo encontrado para esse perióico',
                          response.data.decode('utf-8'))

    def test_issue_grid_with_unknow_journal_id(self):
        """
        Teste para avaliar o retorno da ``view function`` ``issue_grid``
        quando é acessado utilizando um identificador do periódico desconhecido,
        deve retornar status_code 404 com a msg ```Periódico não encontrado``.
        """

        journal = utils.makeOneJournal()

        issues = utils.makeAnyIssue(attrib={'journal': journal.id})

        unknow_id = '9km2g78o2mnu7'

        response = self.client.get(url_for('main.issue_grid',
                                   journal_id=unknow_id))

        self.assertStatus(response, 404)

        self.assertIn(u'Periódico não encontrado',
                      response.data.decode('utf-8'))

    def test_issue_grid_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_grid`` acessando um periódico
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """

        journal = utils.makeOneJournal({'is_public': False,
                                       'unpublish_reason': 'Problema de Direito Autoral'})

        response = self.client.get(url_for('main.issue_grid',
                                           journal_id=journal.id))

        self.assertStatus(response, 404)
        self.assertIn(u'Problema de Direito Autoral',
                      response.data.decode('utf-8'))

    def test_issue_toc(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando a página do fascículo,
        deve retorna status_code 200 e o template ``issue/toc.html``.
        """

        with current_app.app_context():
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue({'number': '31',
                                        'volume': '10'})

            response = self.client.get(url_for('main.issue_toc',
                                       issue_id=issue.id))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/toc.html')
            # self.assertIn(u'Vol. 10 No. 31', response.data.decode('utf-8'))
            self.assertEqual(self.get_context_variable('issue').id, issue.id)

    def test_issue_toc_unknow_issue_id(self):
        """
        Teste para avaliar o retorno da ``view function`` ``issue_toc``
        quando é acessado utilizando um identificador do issue desconhecido,
        deve retorna status_code 404 com a msg ``Fascículo não encontrado``.
        """

        issue = utils.makeOneIssue()
        unknow_id = '9wks9sjdu9j'

        response = self.client.get(url_for('main.issue_toc',
                                   issue_id=unknow_id))

        self.assertStatus(response, 404)
        self.assertIn(u'Fascículo não encontrado', response.data.decode('utf-8'))

    def test_issue_toc_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando um fascículo
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """

        issue = utils.makeOneIssue({
            'is_public': False,
            'unpublish_reason': 'Fascículo incorreto'})

        response = self.client.get(url_for('main.issue_toc',
                                           issue_id=issue.id))

        self.assertStatus(response, 404)
        self.assertIn(u'Fascículo incorreto', response.data.decode('utf-8'))

    def test_issue_toc_with_journal_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando um fascículo
        com atributo is_public=True, porém com um periódico com atributo
        is_public=False deve retorna uma página com ``status_code`` 404 e msg
        cadastrada no atributo ``reason`` do periódico.
        """

        journal = utils.makeOneJournal({
            'is_public': False,
            'unpublish_reason': 'Revista removida da coleção'})
        issue = utils.makeOneIssue({
            'is_public': True,
            'journal': journal.id})

        response = self.client.get(url_for('main.issue_toc',
                                           issue_id=issue.id))

        self.assertStatus(response, 404)
        self.assertIn(u'Revista removida da coleção', response.data.decode('utf-8'))

    def test_issue_feed(self):
        """
        Teste da ``view function`` ``issue_feed``, deve retornar um rss
        que usa o template ``issue/feed_content.html`` e o título do periódico no
        corpo da página.
        """

        with current_app.app_context():
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue({'number': '31',
                                        'volume': '10'})
            articles = utils.makeAnyArticle(
                issue=issue,
                attrib={'journal': issue.journal.id, 'issue': issue.id}
            )

            response = self.client.get(url_for('main.issue_feed',
                                       issue_id=issue.id))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/feed_content.html')
            self.assertIn(u'Vol. 10 No. 31', response.data.decode('utf-8'))

    def test_issue_feed_unknow_issue_id(self):
        """
        Teste para avaliar o retorno da ``view function`` ``issue_feed``
        quando é acessado utilizando um identificador do issue desconhecido,
        deve retorna status_code 404 com a msg ``Fascículo não encontrado``.
        """

        issue = utils.makeOneIssue()
        unknow_id = '9wks9sjdu9j'

        response = self.client.get(url_for('main.issue_feed',
                                   issue_id=unknow_id))

        self.assertStatus(response, 404)
        self.assertIn(u'Fascículo não encontrado', response.data.decode('utf-8'))

    def test_issue_feed_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_feed`` acessando um fascículo
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """

        issue = utils.makeOneIssue({
            'is_public': False,
            'unpublish_reason': 'Fascículo incorreto'})

        response = self.client.get(url_for('main.issue_feed',
                                           issue_id=issue.id))

        self.assertStatus(response, 404)
        self.assertIn(u'Fascículo incorreto', response.data.decode('utf-8'))

    def test_issue_feed_with_journal_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando um fascículo
        com atributo is_public=True, porém com um periódico com atributo
        is_public=False deve retorna uma página com ``status_code`` 404 e msg
        cadastrada no atributo ``reason`` do periódico.
        """

        journal = utils.makeOneJournal({
            'is_public': False,
            'unpublish_reason': 'Revista removida da coleção'})
        issue = utils.makeOneIssue({
            'is_public': True,
            'journal': journal.id})

        response = self.client.get(url_for('main.issue_feed',
                                           issue_id=issue.id))

        self.assertStatus(response, 404)
        self.assertIn(u'Revista removida da coleção', response.data.decode('utf-8'))

    # ARTICLE

    def test_article_detail(self):
        """
        Teste da ``view function`` ``article_detail``, deve retornar uma página
        que usa o template ``article/detail.html``.
        """
        with current_app.app_context():

            collection = utils.makeOneCollection()

            resource = utils.makeOneResource()

            article = utils.makeOneArticle({'title': 'Article Y',
                                            'htmls': [resource]})

            response = self.client.get(url_for('main.article_detail',
                                               article_id=article.id,
                                               lang_code='pt'))
            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')
            self.assertEqual(self.get_context_variable('article').id, article.id)
            self.assertEqual(self.get_context_variable('journal').id, article.journal.id)
            self.assertEqual(self.get_context_variable('issue').id, article.issue.id)

    def test_article_detail_without_articles(self):
        """
        Teste para avaliar o retorno da ``view function`` ``article_detail``
        quando não existe artigos cadastrados deve retornar ``status_code`` 404
        e a msg ``Artigo não encontrado``
        """

        response = self.client.get(url_for('main.article_detail',
                                           article_id='02ksn892hwytd8jh2',
                                           lang_code='pt'))

        self.assertStatus(response, 404)
        self.assertIn(u'Artigo não encontrado', response.data.decode('utf-8'))

    def test_article_detail_with_journal_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``article_detail`` acessando um artigo
        com atributo is_public=True, porém com um periódico com atributo
        is_public=False deve retorna uma página com ``status_code`` 404 e msg
        cadastrada no atributo ``reason`` do periódico.
        """

        journal = utils.makeOneJournal({
            'is_public': False,
            'unpublish_reason': 'Revista removida da coleção'})

        issue = utils.makeOneIssue({
            'is_public': True,
            'journal': journal.id})

        article = utils.makeOneArticle({
            'issue': issue.id,
            'journal': journal.id})

        response = self.client.get(url_for('main.article_detail',
                                           article_id=article.id,
                                           lang_code='pt'))

        self.assertStatus(response, 404)
        self.assertIn(u'Revista removida da coleção', response.data.decode('utf-8'))

    def test_article_detail_with_issue_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``article_detail`` acessando um artigo
        com atributo is_public=False, porém com um periódico com atributo
        is_public=True deve retorna uma página com ``status_code`` 404 e msg
        cadastrada no atributo ``reason`` do fascículo.
        """

        journal = utils.makeOneJournal()

        issue = utils.makeOneIssue({
            'is_public': False,
            'unpublish_reason': 'Facículo rejeitado',
            'journal': journal.id})

        article = utils.makeOneArticle({
            'issue': issue.id,
            'journal': journal.id})

        response = self.client.get(url_for('main.article_detail',
                                           article_id=article.id,
                                           lang_code='pt'))

        self.assertStatus(response, 404)
        self.assertIn(u'Facículo rejeitado', response.data.decode('utf-8'))

    def test_article_detail_with_article_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``article_detail`` acessando um artigo
        com atributo is_public=False, deve retorna uma página com
         ``status_code`` 404 e msg cadastrada no atributo ``reason`` do artigo.
        """

        journal = utils.makeOneJournal()

        issue = utils.makeOneIssue({'journal': journal.id})

        article = utils.makeOneArticle({
            'is_public': False,
            'unpublish_reason': 'Artigo com problemas de licença',
            'issue': issue.id,
            'journal': journal.id})

        response = self.client.get(url_for('main.article_detail',
                                           article_id=article.id,
                                           lang_code='pt'))

        self.assertStatus(response, 404)
        self.assertIn(u'Artigo com problemas de licença', response.data.decode('utf-8'))

    # ABSTRACT

    def test_abstract_detail_without_html(self):
        """
        Teste da ``view function`` ``abstract_detail``, deve retornar uma
        página 404 com a msg ``Resumo do artigo não encontrado``.
        """

        article = utils.makeOneArticle({'title': 'Article Y'})

        response = self.client.get(url_for('main.abstract_detail',
                                           article_id=article.id,
                                           lang_code='pt'))

        self.assertStatus(response, 404)
        self.assertIn(u'Resumo do artigo não encontrado',
                      response.data.decode('utf-8'))

    def test_abstract_detail_without_articles(self):
        """
        Teste da ``view function`` ``abstract_detail`` sem artigos
        cadastrados, deve retornar página 404 com a msg ``Artigo não encontrado``
        """

        response = self.client.get(url_for('main.abstract_detail',
                                           article_id='9ajsd9shwqjks9syd',
                                           lang_code='pt'))

        self.assertStatus(response, 404)
        self.assertIn(u'Resumo não encontrado', response.data.decode('utf-8'))

    def test_abstract_detail_with_article_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``abstract_detail`` acessando o resumo do
        artigo com atributo is_public=False, deve retorna uma página com
         ``status_code`` 404 e msg cadastrada no atributo ``reason`` do artigo.
        """

        journal = utils.makeOneJournal()

        issue = utils.makeOneIssue({'journal': journal.id})

        article = utils.makeOneArticle({
            'is_public': False,
            'unpublish_reason': 'Resumo incorreto',
            'issue': issue.id,
            'journal': journal.id})

        response = self.client.get(url_for('main.abstract_detail',
                                           article_id=article.id,
                                           lang_code='pt'))

        self.assertStatus(response, 404)
        self.assertIn(u'Resumo incorreto', response.data.decode('utf-8'))

    # HOMEPAGE

    def test_collection_sponsors_at_homepage(self):
        """
        acessar na homepage deve mostrar os sponsors no rodapé
        """
        # with
        with current_app.app_context():
            collection = utils.makeOneCollection()
            sponsor1 = utils.makeOneSponsor({'name': 'spo1', 'url': 'http://sponsor1.com', 'logo_url': 'http://sponsor1.com/logo1.png'})
            sponsor2 = utils.makeOneSponsor({'name': 'spo2', 'url': 'http://sponsor2.com', 'logo_url': 'http://sponsor2.com/logo1.png'})
            sponsor3 = utils.makeOneSponsor({'name': 'spo3', 'url': 'http://sponsor2.com', 'logo_url': 'http://sponsor2.com/logo1.png'})
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
            response = self.client.get(url_for('main.collection_list_alpha'))
            # then
            self.assertStatus(response, 200)
            self.assertIn(collection['address1'], response.data.decode('utf-8'))
            self.assertIn(collection['address2'], response.data.decode('utf-8'))
