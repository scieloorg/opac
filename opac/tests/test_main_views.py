# coding: utf-8
import unittest
import flask
import warnings
from flask import url_for, g, current_app

from .base import BaseTestCase

from . import utils


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
        Se cadastra 10 periódicos sem fascículo, deve retornar na interface do
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
                attrib={'journal': journal.id, 'issue': issue.id}
            )

            response = self.client.get(url_for('main.journal_feed',
                                               url_seg=journal.url_segment))

            self.assertTrue(200, response.status_code)
            self.assertTemplateUsed('issue/feed_content.html')

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

    def test_issue_grid(self):
        """
        Teste da ``view function`` ``issue_grid`` acessando a grade de fascículos
        de um periódico, nesse teste deve ser retornado todos os fascículos com
        o atributo is_public=True de um fascículo, sendo que o template deve ser
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
        quando não existe fascículo cadastrado deve retornar ``status_code`` 200
        e a msg ``Nenhum fascículo encontrado para esse perióico``
        """

        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            response = self.client.get(
                url_for('main.issue_grid', url_seg=journal.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/grid.html')

            self.assertIn('Nenhum fascículo encontrado para esse periódico',
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

    def test_issue_toc(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando a página do fascículo,
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
        deve retorna status_code 404 com a msg ``Fascículo não encontrado``.
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
        self.assertIn('Fascículo não encontrado', response.data.decode('utf-8'))

    def test_issue_toc_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando um fascículo
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """
        unpublish_reason = 'Fascículo incorreto'
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
        Teste da ``view function`` ``issue_toc`` acessando um fascículo
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

    def test_issue_feed_unknow_issue_id(self):
        """
        Teste para avaliar o retorno da ``view function`` ``issue_feed``
        quando é acessado utilizando um identificador do issue desconhecido,
        deve retorna status_code 404 com a msg ``Fascículo não encontrado``.
        """
        journal = utils.makeOneJournal()

        utils.makeOneIssue({'journal': journal})

        unknow_url_seg = '2015.v6n3'

        response = self.client.get(url_for('main.issue_feed',
                                   url_seg=journal.url_segment,
                                   url_seg_issue=unknow_url_seg))

        self.assertStatus(response, 404)
        self.assertIn('Fascículo não encontrado', response.data.decode('utf-8'))

    def test_issue_feed_with_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_feed`` acessando um fascículo
        com atributo is_public=False, deve retorna uma página com ``status_code``
        404 e msg cadastrada no atributo ``reason``.
        """

        unpublish_reason = 'Fascículo incorreto'
        journal = utils.makeOneJournal()
        issue = utils.makeOneIssue({
            'is_public': False,
            'unpublish_reason': unpublish_reason,
            'journal': journal})

        response = self.client.get(url_for('main.issue_feed',
                                           url_seg=journal.url_segment,
                                           url_seg_issue=issue.url_segment))

        self.assertStatus(response, 404)
        self.assertIn('Fascículo incorreto', response.data.decode('utf-8'))

    def test_issue_feed_with_journal_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``issue_toc`` acessando um fascículo
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

    def test_article_detail(self):
        """
        Teste da ``view function`` ``article_detail``, deve retornar uma página
        que usa o template ``article/detail.html``.
        """
        with current_app.app_context():

            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            article = utils.makeOneArticle({'title': 'Article Y',
                                            'issue': issue,
                                            'journal': journal,
                                            'url_segment': '10-11'})

            response = self.client.get(url_for('main.article_detail',
                                               url_seg=journal.url_segment,
                                               url_seg_issue=issue.url_segment,
                                               url_seg_article=article.url_segment,
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

        journal = utils.makeOneJournal()

        issue = utils.makeOneIssue({'journal': journal})

        response = self.client.get(url_for('main.article_detail',
                                           url_seg=journal.url_segment,
                                           url_seg_issue=issue.url_segment,
                                           url_seg_article='9827-817',
                                           lang_code='pt'))

        self.assertStatus(response, 404)
        self.assertIn('Artigo não encontrado', response.data.decode('utf-8'))

    def test_article_detail_with_journal_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``article_detail`` acessando um artigo
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

        response = self.client.get(url_for('main.article_detail',
                                           url_seg=journal.url_segment,
                                           url_seg_issue=issue.url_segment,
                                           url_seg_article=article.url_segment,
                                           lang_code='pt'))

        self.assertStatus(response, 404)
        self.assertIn(unpublish_reason, response.data.decode('utf-8'))

    def test_article_detail_with_issue_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``article_detail`` acessando um artigo
        com atributo is_public=False, porém com um periódico com atributo
        is_public=True deve retorna uma página com ``status_code`` 404 e msg
        cadastrada no atributo ``reason`` do fascículo.
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

        response = self.client.get(url_for('main.article_detail',
                                           url_seg=journal.url_segment,
                                           url_seg_issue=issue.url_segment,
                                           url_seg_article=article.url_segment,
                                           lang_code='pt'))

        self.assertStatus(response, 404)
        self.assertIn(unpublish_reason, response.data.decode('utf-8'))

    def test_article_detail_with_article_attrib_is_public_false(self):
        """
        Teste da ``view function`` ``article_detail`` acessando um artigo
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

        response = self.client.get(url_for('main.article_detail',
                                           url_seg=journal.url_segment,
                                           url_seg_issue=issue.url_segment,
                                           url_seg_article=article.url_segment,
                                           lang_code='pt'))

        self.assertStatus(response, 404)
        self.assertIn(unpublish_reason, response.data.decode('utf-8'))

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
            response = self.client.get(url_for('main.collection_list'))
            # then
            self.assertStatus(response, 200)
            self.assertIn(collection['address1'], response.data.decode('utf-8'))
            self.assertIn(collection['address2'], response.data.decode('utf-8'))
