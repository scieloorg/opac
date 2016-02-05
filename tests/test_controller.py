# coding: utf-8

from uuid import uuid4

from base import BaseTestCase

from opac_schema.v1 import models

from app import controllers

import utils


class JournalControllerTestCase(BaseTestCase):

    def _makeOne(self, attrib=None):
        """
        Retorna um objeto ``Journal`` com os atributos obrigatórios:
        ``_id``, ``jid``, ``is_public``, o param ``attrib`` atualiza os
        atributos do objeto.
        """
        return utils.makeOneJournal(attrib=attrib)

    def _makeAny(self, items=3):
        """
        Retorna uma lista de objetos ``Journal`` com atributos ``jid``,
        ``is_public`` e ``acronym`` limitando a quantidade pelo param ``items``.
        """
        return utils.makeAnyJournal(items=items)

    def tearDown(self):
        """
        Remove todos os objectos ``Journal`` ao terminar cada teste.
        """
        models.Journal.objects.delete()

    def test_get_journal(self):
        """
        Teste da função controllers.get_journals() para retornar um objeto:
        ``Journal``.
        """
        journal = self._makeOne()
        self.assertEqual(controllers.get_journals()[0], journal)

    def test_get_public_journal(self):
        """
        Teste da função controllers.get_journals() para retorna um objeto:
        ``Journal`` explicitanto o artibuto is_public=True.
        """
        journal = self._makeOne()
        self.assertEqual(controllers.get_journals(is_public=True)[0], journal)

    def test_get_not_public_journal(self):
        """
        Teste da função controllers.get_journals() para retorna um objeto:
        ``Journal`` explicitanto o artibuto is_public=False.
        """
        journal = self._makeOne({'is_public': False})
        self.assertEqual(controllers.get_journals(is_public=False)[0], journal)

    def test_get_journal_order_by_acronym(self):
        """
        Teste da função controllers.get_journals() para retorna um objeto:
        ``Journal`` considerando a ordenação por acrônimo.
        """
        journalC = self._makeOne({'acronym': 'revistaC'})
        journalA = self._makeOne({'acronym': 'revistaA'})
        journalB = self._makeOne({'acronym': 'revistaB'})

        self.assertListEqual(
            [journal for journal in controllers.get_journals(order_by='acronym')],
            [journalA, journalB, journalC])

    def test_get_journal_without_itens(self):
        """
        Testando a função controllers.get_journals() com uma coleção de Journal
        vazia, deve retornar ``None``.
        """
        self.assertFalse(controllers.get_journals())

    def test_get_journals_by_study_area(self):
        """
        Testando se o retorno da função controllers.get_journals_by_study_area()
        está de acordo com o esperado.
        """

        journal1 = self._makeOne({"study_areas": ["Health Sciences"]})

        journal2 = self._makeOne({"study_areas": ["Health Sciences",
                                  "Biological Sciences"]})
        journal3 = self._makeOne({"study_areas": ["Exact and Earth Sciences"]})
        journal4 = self._makeOne({"study_areas": ["Human Sciences",
                                  "Biological Sciences", "Engineering"]})
        journal5 = self._makeOne({"study_areas": ["Linguistics"]})
        journal6 = self._makeOne({"study_areas": ["Engineering"]})

        expected = {
                    'meta': {'total': 6},
                    'objects': {
                        u'Health Sciences': [journal1, journal2],
                        u'Engineering': [journal4, journal6],
                        u'Biological Sciences': [journal2, journal4],
                        u'Linguistics': [journal5],
                        u'Human Sciences': [journal4],
                        u'Exact and Earth Sciences': [journal3]
                    }
                }

        study_areas = controllers.get_journals_by_study_area()

        self.assertEqual(expected['meta']['total'], study_areas['meta']['total'])

        self.assertEqual(len(expected['objects']), len(study_areas['objects']))

        for area, journals in expected['objects'].iteritems():
            self.assertListEqual(sorted([journal.id for journal in expected['objects'][area]]),
                                 sorted([journal.id for journal in journals]))

    def test_get_journals_by_study_area_without_journal(self):
        """
        Testando controllers.get_journals_by_study_area() sem Journal
        """

        expected = {
                    'meta': {'total': 0},
                    'objects': {
                    }
                }

        study_areas = controllers.get_journals_by_study_area()

        self.assertEqual(expected['meta']['total'], study_areas['meta']['total'])

        self.assertEqual(len(expected['objects']), len(study_areas['objects']))

    def test_get_journals_by_indexer(self):
        """
        Testando se o retorno da função controllers.get_journals_by_indexer()
        está de acordo com o esperado.
        """

        journal1 = self._makeOne({"index_at": ["SCIE"]})
        journal2 = self._makeOne({"index_at": ["SCIE", "SSCI"]})
        journal3 = self._makeOne({"index_at": ["SCIE"]})
        journal4 = self._makeOne({"index_at": ["SSCI", "ICSE"]})
        journal5 = self._makeOne({"index_at": ["SSCI", "SCIE"]})
        journal6 = self._makeOne({"index_at": ["SSCI"]})

        expected = {
                    'meta': {'total': 6},
                    'objects': {
                        u'SCIE': [journal1, journal2, journal3, journal5],
                        u'SSCI': [journal2, journal4, journal5],
                        u'ICSE': [journal4]
                    }
                }

        study_areas = controllers.get_journals_by_indexer()

        self.assertEqual(expected['meta']['total'], study_areas['meta']['total'])

        self.assertEqual(len(expected['objects']), len(study_areas['objects']))

        for area, journals in expected['objects'].iteritems():
            self.assertListEqual(sorted([journal.id for journal in expected['objects'][area]]),
                                 sorted([journal.id for journal in journals]))

    def test_get_journals_by_indexer_without_journal(self):
        """
        Testando controllers.test_get_journals_by_indexer() sem Journal.
        """
        expected = {
                    'meta': {'total': 0},
                    'objects': {}
                }

        study_areas = controllers.get_journals_by_indexer()

        self.assertEqual(expected['meta']['total'], study_areas['meta']['total'])

        self.assertEqual(len(expected['objects']), len(study_areas['objects']))

    def test_get_journals_by_sponsor(self):
        """
        Testando se o retorno da função controllers.get_journals_by_sponsor()
        está de acordo com o esperado.
        """

        journal1 = self._makeOne({"sponsors": ["CNPQ"]})
        journal2 = self._makeOne({"sponsors": ["SciELO", "FAPESP"]})
        journal3 = self._makeOne({"sponsors": ["FAPESP", "SciELO"]})
        journal4 = self._makeOne({"sponsors": ["FUNDAÇÃO XPTO", "SciELO"]})
        journal5 = self._makeOne({"sponsors": ["FAPESP", "SciELO"]})
        journal6 = self._makeOne({"sponsors": ["FUNDAÇÃO XPTO"]})

        expected = {
                    'meta': {'total': 6},
                    'objects': {
                        u'CNPQ': [journal1],
                        u'SciELO': [journal2, journal3, journal4, journal5],
                        u'FAPESP': [journal4],
                        u'FUNDAÇÃO XPTO': [journal4, journal6]
                    }
                }

        study_areas = controllers.get_journals_by_sponsor()

        self.assertEqual(expected['meta']['total'], study_areas['meta']['total'])

        self.assertEqual(len(expected['objects']), len(study_areas['objects']))

        for area, journals in expected['objects'].iteritems():
            self.assertListEqual(sorted([journal.id for journal in expected['objects'][area]]),
                                 sorted([journal.id for journal in journals]))

    def test_get_journals_by_sponsor_without_journal(self):
        """
        Testando controllers.get_journals_by_sponsor() sem journal.
        """

        expected = {
                    'meta': {'total': 0},
                    'objects': {}
                }

        study_areas = controllers.get_journals_by_sponsor()

        self.assertEqual(expected['meta']['total'], study_areas['meta']['total'])

        self.assertEqual(len(expected['objects']), len(study_areas['objects']))

    def test_get_journal_by_jid(self):
        """
        Testando a função controllers.get_journal_by_jid() deve retornar um
        objeto ``Journal`` com o id=jid123.
        """
        journal = self._makeOne(attrib={'_id': 'jid123'})

        self.assertEqual(controllers.get_journal_by_jid('jid123').id,
                         journal.id)

    def test_get_journal_by_jid_with_some_params(self):
        """
        Testando a função controllers.get_journal_by_jid() deve retornar um
        objeto ``Journal`` com o id=jid123 e com is_public=false.
        """
        journal1 = self._makeOne(attrib={'_id': 'jid1', 'is_public': True})
        journal2 = self._makeOne(attrib={'_id': 'jid2', 'is_public': True})
        journal3 = self._makeOne(attrib={'_id': 'jid3', 'is_public': False})
        journal4 = self._makeOne(attrib={'_id': 'jid4', 'is_public': False})

        self.assertEqual(controllers.get_journal_by_jid('jid3',
                         is_public=False).id, journal3.id)

    def test_get_journal_by_jid_without_journal(self):
        """
        Testando controllers.get_journal_by_jid() sem journal, deve retornar
        None
        """
        self.assertIsNone(controllers.get_journal_by_jid('anyjid'))

    def test_get_journals_by_jid(self):
        """
        Testando a função controllers.get_journals_by_jid() deve retornar uma
        lista contendo objetos ``Journal`` .
        """

        self._makeAny(items=5)

        self._makeOne(attrib={'_id': 'jid1'})
        self._makeOne(attrib={'_id': 'jid12'})
        self._makeOne(attrib={'_id': 'jid123'})

        self._makeAny(items=5)

        journals = controllers.get_journals_by_jid(['jid1', 'jid12', 'jid123'])

        expected = [u'jid1', u'jid12', u'jid123']

        self.assertListEqual(sorted([journal for journal in journals.iterkeys()]),
                             sorted(expected))

    def test_get_journals_by_jid_with_not_found_jids(self):
        """
        Testando a função controllers.get_journals_by_jid() deve retornar uma
        lista contendo objetos ``Journal`` .
        """

        self._makeAny(items=5)

        self._makeOne(attrib={'_id': 'jid1'})
        self._makeOne(attrib={'_id': 'jid12'})
        self._makeOne(attrib={'_id': 'jid123'})

        self._makeAny(items=5)

        journals = controllers.get_journals_by_jid(['k8u1jid1', '0823mgjid12',
                                                   '-012-js7jid123'])

        self.assertIsNone(journals)

    def test_get_journals_by_jid_without_journal(self):
        """
        Testando controllers.get_journals_by_jid() sem journal, deve retornar
        None.
        """

        journals = controllers.get_journals_by_jid(['jid1', 'jid12', 'jid123'])

        self.assertIsNone(journals)


class IssueControllerTestCase(BaseTestCase):

    def _makeOne(self, attrib=None):
        """
        Retorna um objeto ``Issue`` com os atributos obrigatórios:
        ``_id``, ``jid``, ``is_public`` e ``journal``, o param ``attrib`` atualiza os
        atributos do objeto.
        """
        return utils.makeOneIssue(attrib=attrib)

    def _makeAny(self, journal=None, items=3):
        """
        Retorna uma lista de objetos ``Journal`` com atributos ``jid``,
        ``is_public`` e ``acronym`` limitando a quantidade pelo param ``items``.
        """
        return utils.makeAnyIssue(journal=journal, items=items)

    def tearDown(self):
        """
        Remove todos os objectos ``Issue`` ao terminar cada teste.
        """
        models.Journal.objects.delete()
        models.Issue.objects.delete()

    def test_get_issues_by_jid(self):
        """
        Teste da função controllers.get_issue_by_jid() para retornar um objeto:
        ``Issue``.
        """

        issue = self._makeOne()

        self.assertEqual(controllers.get_issues_by_jid(issue.journal.id)[0].id,
                         issue.id)

    def test_get_issues_by_jid_with_many_items(self):
        """
        Teste da função controllers.get_issue_by_jid() com vários itens, deve
        deve retorna uma lista.
        """

        journal = utils.makeOneJournal()

        self._makeOne({'_id': '1', 'journal': journal.id})
        self._makeOne({'_id': '2', 'journal': journal.id})
        self._makeOne({'_id': '3', 'journal': journal.id})
        self._makeOne({'_id': '4', 'journal': journal.id})

        issues = [issue.id for issue in controllers.get_issues_by_jid(journal.id)]

        self.assertListEqual(sorted(issues), sorted(['1', '2', '3', '4']))

    def test_get_issues_by_jid_changing_default_order_by(self):
        """
        Teste da função controllers.get_issue_by_jid() com vários itens, deve
        deve retorna uma lista considerando o valor explicito do atributo
        ``order_by``
        """

        journal = utils.makeOneJournal()

        self._makeOne({'_id': '1', 'journal': journal.id, 'number': '10'})
        self._makeOne({'_id': '2', 'journal': journal.id, 'number': '9'})
        self._makeOne({'_id': '3', 'journal': journal.id, 'number': '8'})
        self._makeOne({'_id': '4', 'journal': journal.id, 'number': '7'})

        issues = [issue.id for issue in controllers.get_issues_by_jid(journal.id, order_by=['number'])]

        self.assertListEqual(sorted(issues), sorted(['4', '3', '2', '1']))

    def test_get_issue_by_iid(self):
        """
        Teste da função controllers.get_issue_by_iid() para retornar um objeto:
        ``Issue``.
        """
        issue = self._makeOne()
        self.assertEqual(controllers.get_issue_by_iid(issue.id), issue)

    def test_get_issue_by_iid_with_some_params(self):
        """
        Teste da função controllers.get_issue_by_iid() para retornar um objeto:
        ``Issue``.
        """
        issue = self._makeOne({'volume': '10', 'number': '4'})

        self._makeAny(items=30)

        self.assertEqual(controllers.get_issue_by_iid(issue.id, volume='10',
                         number='4'), issue)

    def test_get_issues_by_iid(self):
        """
        Testando a função controllers.get_issues_by_iid() deve retornar uma
        lista contendo objetos ``Issue``.
        """

        self._makeAny(items=5)

        self._makeOne(attrib={'_id': 'iid1'})
        self._makeOne(attrib={'_id': 'iid12'})
        self._makeOne(attrib={'_id': 'iid123'})

        self._makeAny(items=5)

        issues = controllers.get_issues_by_iid(['iid1', 'iid12', 'iid123'])

        expected = [u'iid1', u'iid12', u'iid123']

        self.assertListEqual(sorted([issue for issue in issues.iterkeys()]),
                             sorted(expected))

    def test_get_issues_by_iid_without_issue(self):
        """
        Testando controllers.get_issues_by_iid() sem issue, deve retornar None.
        """

        issues = controllers.get_issues_by_iid(['iid1', 'iid12', 'iid123'])

        self.assertIsNone(issues)

    def test_set_issue_is_public_bulk(self):
        """
        Testando alterar o valor de um conjunto de issues.
        """

        self._makeOne(attrib={'_id': '012ijs9y24', 'is_public': True})
        self._makeOne(attrib={'_id': '2183ikos90', 'is_public': True})
        self._makeOne(attrib={'_id': '9298wjso89', 'is_public': True})

        controllers.set_issue_is_public_bulk(
            ['012ijs9y24', '2183ikos90', '9298wjso89'], is_public=False)

        ids = ['012ijs9y24', '2183ikos90', '9298wjso89']

        issues = controllers.get_issues_by_iid(ids)

        for issue in issues.itervalues():
            self.assertFalse(issue.is_public)

    def test_set_issue_is_public_bulk_setting_reason(self):
        """
        Testando alterar o valor de um conjunto de issues com o motivo, param
        ``reason``.
        """

        self._makeOne(attrib={'_id': '012ijs9y24', 'is_public': True})
        self._makeOne(attrib={'_id': '2183ikos90', 'is_public': True})
        self._makeOne(attrib={'_id': '9298wjso89', 'is_public': True})

        ids = ['012ijs9y24', '2183ikos90', '9298wjso89']

        controllers.set_issue_is_public_bulk(ids, is_public=False,
                                             reason='plágio')

        issues = controllers.get_issues_by_iid(ids)

        for issue in issues.itervalues():
            self.assertEqual(u'plágio', issue.unpublish_reason)


class ArticleControllerTestCase(BaseTestCase):

    def _makeOne(self, attrib=None):
        """
        Retorna um objeto ``Article`` com os atributos obrigatórios:
        ``_id``, ``jid``, ``is_public`` e ``issue`` o param ``attrib`` atualiza
        os atributos do objeto.
        """
        return utils.makeOneArticle(attrib=attrib)

    def _makeAny(self, issue=None, items=3):
        """
        Retorna uma lista de objetos ``Article`` com atributos ``jid``,
        ``is_public`` e ``acronym`` limitando a quantidade pelo param ``items``.
        """
        return utils.makeAnyArticle(issue=issue, items=items)

    def tearDown(self):
        """
        Remove todos os objectos ``Article`` ao terminar cada teste.
        """
        models.Journal.objects.delete()
        models.Issue.objects.delete()
        models.Article.objects.delete()

    def test_get_article_by_aid(self):
        """
        Teste da função controllers.get_article_by_aid para retornar um objeto:
        ``Article``.
        """

        article = self._makeOne()

        self.assertEqual(controllers.get_article_by_aid(article.id).id,
                         article.id)

    def test_get_article_by_aid_without_article(self):
        """
        Testando controllers.get_article_by_aid() sem article, deve retornar
        None.
        """
        self.assertIsNone(controllers.get_article_by_aid('anyjid'))

    def test_get_articles_by_aid(self):
        """
        Testando a função controllers.get_articles_by_aid() deve retornar uma
        lista contendo objetos ``Article`` .
        """

        self._makeAny(items=5)

        self._makeOne(attrib={'_id': 'aid1'})
        self._makeOne(attrib={'_id': 'aid12'})
        self._makeOne(attrib={'_id': 'aid123'})

        self._makeAny(items=5)

        articles = controllers.get_articles_by_aid(['aid1', 'aid12', 'aid123'])

        expected = [u'aid1', u'aid12', u'aid123']

        self.assertListEqual(sorted([article for article in articles.iterkeys()]),
                             sorted(expected))

    def test_get_articles_by_aid_with_not_found_jids(self):
        """
        Testando a função controllers.get_articles_by_aid() deve retornar um
        None.
        """

        self._makeAny(items=5)

        self._makeOne(attrib={'_id': 'aid1'})
        self._makeOne(attrib={'_id': 'aid12'})
        self._makeOne(attrib={'_id': 'aid123'})

        self._makeAny(items=5)

        articles = controllers.get_journals_by_jid(['k8u1jid1', '0823mgjid12',
                                                   '-012-js7jid123'])

        self.assertIsNone(articles)

    def test_get_articles_by_aid_without_article(self):
        """
        Testando controllers.get_articles_by_aid() sem article, deve retornar
        None.
        """

        articles = controllers.get_articles_by_aid(['aid1', 'aid12', 'aid123'])

        self.assertIsNone(articles)

    def test_set_article_is_public_bulk(self):
        """
        Testando alterar o valor de um conjunto de article
        """

        self._makeOne(attrib={'_id': '012ijs9y24', 'is_public': True})
        self._makeOne(attrib={'_id': '2183ikos90', 'is_public': True})
        self._makeOne(attrib={'_id': '9298wjso89', 'is_public': True})

        controllers.set_article_is_public_bulk(
            ['012ijs9y24', '2183ikos90', '9298wjso89'], is_public=False)

        ids = ['012ijs9y24', '2183ikos90', '9298wjso89']

        articles = controllers.get_articles_by_aid(ids)

        for article in articles.itervalues():
            self.assertFalse(article.is_public)

    def test_get_articles_by_iid(self):
        """
        Testando a função controllers.get_articles_by_iid(), deve retorna uma
        lista de articles.
        """

        self._makeOne(attrib={'_id': '012ijs9y24', 'issue': '90210j83'})
        self._makeOne(attrib={'_id': '2183ikos90', 'issue': '90210j83'})
        self._makeOne(attrib={'_id': '9298wjso89', 'issue': '90210j82'})

        expected = [u'012ijs9y24', u'2183ikos90']

        articles = [article.id for article in controllers.get_articles_by_iid('90210j83')]

        self.assertListEqual(sorted(articles), sorted(expected))
