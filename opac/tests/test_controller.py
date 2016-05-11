# coding: utf-8

from uuid import uuid4

from werkzeug.security import check_password_hash

from base import BaseTestCase

from opac_schema.v1 import models

from webapp import controllers, dbsql, utils as ut

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
        vazia, deve retornar uma lista vazia.
        """
        self.assertEqual(len(controllers.get_journals()), 0)

    def test_get_journals_grouped_by_study_area(self):
        """
        Testando se o retorno da função controllers.get_journals_by_study_area()
        está de acordo com o esperado.
        """

        journal1 = self._makeOne({
            "study_areas": ["Health Sciences"],
            "last_issue": {"volume": "1", "number": "1", "year": "2016"}
        })
        journal2 = self._makeOne({
            "study_areas": ["Health Sciences", "Biological Sciences"],
            "last_issue": {"volume": "2", "number": "2", "year": "2016"}
        })
        journal3 = self._makeOne({
            "study_areas": ["Exact and Earth Sciences"],
            "last_issue": {"volume": "3", "number": "3", "year": "2016"}
        })
        journal4 = self._makeOne({
            "study_areas": ["Human Sciences", "Biological Sciences", "Engineering"],
            "last_issue": {"volume": "4", "number": "4", "year": "2016"}
        })
        journal5 = self._makeOne({
            "study_areas": ["Linguistics"],
            "last_issue": {"volume": "5", "number": "5", "year": "2016"}
        })
        journal6 = self._makeOne({
            "study_areas": ["Engineering"],
            "last_issue": {"volume": "6", "number": "6", "year": "2016"}
        })

        expected = {
            'meta': {
                'total': 6,
                'themes_count': 6
            },
            'objects': {
                u'Health Sciences': [
                    controllers.get_journal_json_data(journal1),
                    controllers.get_journal_json_data(journal2)
                ],
                u'Engineering': [
                    controllers.get_journal_json_data(journal4),
                    controllers.get_journal_json_data(journal6)
                ],
                u'Biological Sciences': [
                    controllers.get_journal_json_data(journal2),
                    controllers.get_journal_json_data(journal4)
                ],
                u'Linguistics': [
                    controllers.get_journal_json_data(journal5)
                ],
                u'Human Sciences': [
                    controllers.get_journal_json_data(journal4)
                ],
                u'Exact and Earth Sciences': [
                    controllers.get_journal_json_data(journal3)
                ]
            }
        }

        grouped_objects = controllers.get_journals_grouped_by('study_areas')

        self.assertEqual(expected['meta']['total'], grouped_objects['meta']['total'])
        self.assertEqual(expected['meta']['themes_count'], grouped_objects['meta']['themes_count'])
        self.assertEqual(len(expected['objects']), len(grouped_objects['objects']))

        for grouper, journals in expected['objects'].iteritems():
            self.assertListEqual(sorted([journal['id'] for journal in expected['objects'][grouper]]),
                                 sorted([journal['id'] for journal in journals]))

    def test_get_journals_grouped_by_study_areas_without_journals(self):
        """
        Testando controllers.get_journals_grouped_by('study_areas') sem Journal
        """

        expected = {
            'meta': {
                'total': 0,
                'themes_count': 0
            },
            'objects': {}
        }

        grouped_objects = controllers.get_journals_grouped_by('study_areas')

        self.assertEqual(expected['meta']['total'], grouped_objects['meta']['total'])
        self.assertEqual(expected['meta']['themes_count'], grouped_objects['meta']['themes_count'])
        self.assertEqual(len(expected['objects']), len(grouped_objects['objects']))

    def test_get_journals_grouped_by_index_at(self):
        """
        Testando se o retorno da função controllers.get_journals_grouped_by('index_at')
        está de acordo com o esperado.
        """

        journal1 = self._makeOne({
            "index_at": ["SCIE"],
            "last_issue": {"volume": "1", "number": "1", "year": "2016"}
        })
        journal2 = self._makeOne({
            "index_at": ["SCIE", "SSCI"],
            "last_issue": {"volume": "2", "number": "2", "year": "2016"}
        })
        journal3 = self._makeOne({
            "index_at": ["SCIE"],
            "last_issue": {"volume": "3", "number": "3", "year": "2016"}
        })
        journal4 = self._makeOne({
            "index_at": ["SSCI", "ICSE"],
            "last_issue": {"volume": "4", "number": "4", "year": "2016"}
        })
        journal5 = self._makeOne({
            "index_at": ["SSCI", "SCIE"],
            "last_issue": {"volume": "5", "number": "5", "year": "2016"}
        })
        journal6 = self._makeOne({
            "index_at": ["SSCI"],
            "last_issue": {"volume": "6", "number": "6", "year": "2016"}
        })

        expected = {
            'meta': {
                'total': 6,
                'themes_count': 3
            },
            'objects': {
                u'SCIE': [
                    controllers.get_journal_json_data(journal1),
                    controllers.get_journal_json_data(journal2),
                    controllers.get_journal_json_data(journal3),
                    controllers.get_journal_json_data(journal5)
                ],
                u'SSCI': [
                    controllers.get_journal_json_data(journal2),
                    controllers.get_journal_json_data(journal4),
                    controllers.get_journal_json_data(journal5)
                ],
                u'ICSE': [
                    controllers.get_journal_json_data(journal4)
                ]
            }
        }

        grouped_objects = controllers.get_journals_grouped_by('index_at')

        self.assertEqual(expected['meta']['total'], grouped_objects['meta']['total'])
        self.assertEqual(expected['meta']['themes_count'], grouped_objects['meta']['themes_count'])
        self.assertEqual(len(expected['objects']), len(grouped_objects['objects']))
        for grouper, journals in expected['objects'].iteritems():
            self.assertListEqual(sorted([journal['id'] for journal in expected['objects'][grouper]]),
                                 sorted([journal['id'] for journal in journals]))

    def test_get_journals_grouped_by_index_at_without_journal(self):
        """
        Testando controllers.get_journals_grouped_by('index_at') sem Journal.
        """
        expected = {
            'meta': {
                'total': 0,
                'themes_count': 0
            },
            'objects': {}
        }

        grouped_objects = controllers.get_journals_grouped_by('index_at')

        self.assertEqual(expected['meta']['total'], grouped_objects['meta']['total'])
        self.assertEqual(expected['meta']['themes_count'], grouped_objects['meta']['themes_count'])
        self.assertEqual(len(expected['objects']), len(grouped_objects['objects']))

    def test_get_journals_grouped_by_publisher_name(self):
        """
        Testando se o retorno da função controllers.get_journals_grouped_by('publisher_name')
        está de acordo com o esperado.
        """

        journal1 = self._makeOne({
            "publisher_name": "CNPQ",
            "last_issue": {"volume": "1", "number": "1", "year": "2016"}
        })
        journal2 = self._makeOne({
            "publisher_name": "SciELO",
            "last_issue": {"volume": "2", "number": "2", "year": "2016"}
        })
        journal3 = self._makeOne({
            "publisher_name": "FAPESP",
            "last_issue": {"volume": "3", "number": "3", "year": "2016"}
        })
        journal4 = self._makeOne({
            "publisher_name": "FUNDAÇÃO XPTO",
            "last_issue": {"volume": "4", "number": "4", "year": "2016"}
        })
        journal5 = self._makeOne({
            "publisher_name": "FAPESP",
            "last_issue": {"volume": "5", "number": "5", "year": "2016"}
        })
        journal6 = self._makeOne({
            "publisher_name": "FUNDAÇÃO XPTO",
            "last_issue": {"volume": "6", "number": "6", "year": "2016"}
        })

        expected = {
            'meta': {
                'total': 6,
                'themes_count': 4
            },
            'objects': {
                u'CNPQ': [
                    controllers.get_journal_json_data(journal1)
                ],
                u'SciELO': [
                    controllers.get_journal_json_data(journal2),
                    controllers.get_journal_json_data(journal3),
                    controllers.get_journal_json_data(journal4),
                    controllers.get_journal_json_data(journal5)
                ],
                u'FAPESP': [
                    controllers.get_journal_json_data(journal4)
                ],
                u'FUNDAÇÃO XPTO': [
                    controllers.get_journal_json_data(journal4),
                    controllers.get_journal_json_data(journal6)
                ]
            }
        }

        grouped_objects = controllers.get_journals_grouped_by('publisher_name')

        self.assertEqual(expected['meta']['total'], grouped_objects['meta']['total'])
        self.assertEqual(expected['meta']['themes_count'], grouped_objects['meta']['themes_count'])
        self.assertEqual(len(expected['objects']), len(grouped_objects['objects']))

        for grouper, journals in expected['objects'].iteritems():
            self.assertListEqual(sorted([journal['id'] for journal in expected['objects'][grouper]]),
                                 sorted([journal['id'] for journal in journals]))

    def test_get_journals_grouped_by_publisher_name_without_journal(self):
        """
        Testando controllers.get_journals_grouped_by('publisher_name') sem periódicos.
        """

        expected = {
            'meta': {
                'total': 0,
                'themes_count': 0
            },
            'objects': {}
        }

        grouped_objects = controllers.get_journals_grouped_by('publisher_name')

        self.assertEqual(expected['meta']['total'], grouped_objects['meta']['total'])
        self.assertEqual(expected['meta']['themes_count'], grouped_objects['meta']['themes_count'])
        self.assertEqual(len(expected['objects']), len(grouped_objects['objects']))

    def test_get_journal_by_jid(self):
        """
        Testando a função controllers.get_journal_by_jid() deve retornar um
        objeto ``Journal`` com o id=jid123.
        """
        journal = self._makeOne(attrib={'_id': 'jid123'})

        self.assertEqual(controllers.get_journal_by_jid('jid123').id,
                         journal.id)

    def test_get_journal_by_jid_without_id(self):
        """
        Testando a função controllers.get_journal_by_jid() com uma lista vazia,
        deve retorna um exceção ValueError.
        """

        self.assertRaises(ValueError, controllers.get_journal_by_jid, [])

    def test_get_journal_by_jid_with_some_params(self):
        """
        Testando a função controllers.get_journal_by_jid() deve retornar um
        objeto ``Journal`` com o id=jid123 e com is_public=false.
        """
        journal1 = self._makeOne(attrib={'_id': 'jid1', 'is_public': True})
        journal2 = self._makeOne(attrib={'_id': 'jid2', 'is_public': True})
        journal3 = self._makeOne(attrib={'_id': 'jid3', 'is_public': False})
        journal4 = self._makeOne(attrib={'_id': 'jid4', 'is_public': False})

        self.assertEqual(
            controllers.get_journal_by_jid('jid3', is_public=False).id,
            journal3.id)

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

        self.assertEqual(journals, {})

    def test_get_journals_by_jid_without_journal(self):
        """
        Testando controllers.get_journals_by_jid() sem journal, deve retornar
        None.
        """

        journals = controllers.get_journals_by_jid(['jid1', 'jid12', 'jid123'])

        self.assertEqual(journals, {})

    def test_set_journal_is_public_bulk(self):
        """
        Testando alterar o valor de um conjunto de journals.
        """

        self._makeOne(attrib={'_id': 'okls9slqwj', 'is_public': True})
        self._makeOne(attrib={'_id': 'kaomkwisdp', 'is_public': True})
        self._makeOne(attrib={'_id': '0wklwmnsiu', 'is_public': True})

        controllers.set_journal_is_public_bulk(
            ['okls9slqwj', 'kaomkwisdp', '0wklwmnsiu'], is_public=False)

        ids = ['okls9slqwj', 'kaomkwisdp', '0wklwmnsiu']

        journals = controllers.get_journals_by_jid(ids)

        for journal in journals.itervalues():
            self.assertFalse(journal.is_public)

    def test_set_journal_is_public_bulk_without_jids(self):
        """
        Testando alterar o valor de um conjunto de journals, sem ids.
        """

        self._makeOne(attrib={'_id': 'okls9slqwj', 'is_public': True})
        self._makeOne(attrib={'_id': 'kaomkwisdp', 'is_public': True})
        self._makeOne(attrib={'_id': '0wklwmnsiu', 'is_public': True})

        self.assertRaises(ValueError,
                          controllers.set_journal_is_public_bulk, [], is_public=False)

        ids = ['okls9slqwj', 'kaomkwisdp', '0wklwmnsiu']

        journals = controllers.get_journals_by_jid(ids)

        for journal in journals.itervalues():
            self.assertTrue(journal.is_public)


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

    def test_get_issues_by_jid_with_unknow_ids(self):
        """
        Teste da função controllers.get_issue_by_jid() com um jid desconhecido,
        deve retornar um None.
        """

        issues = controllers.get_issues_by_jid('02i28wjs92u')

        self.assertIsNone(issues)

    def test_get_issue_by_iid(self):
        """
        Teste da função controllers.get_issue_by_iid() para retornar um objeto:
        ``Issue``.
        """
        issue = self._makeOne()
        self.assertEqual(controllers.get_issue_by_iid(issue.id), issue)

    def test_get_issue_by_iid_without_id(self):
        """
        Teste da função controllers.get_issue_by_iid() com uma lista vazia,
        deve retorna um exceção ValueError.
        """
        self.assertRaises(ValueError, controllers.get_issue_by_iid, [])

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

        self.assertEqual(issues, {})

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

    def test_set_issue_is_public_bulk_without_iids(self):
        """
        Testando alterar o valor de um conjunto de journals, sem ids.
        """

        self._makeOne(attrib={'_id': '0ow9sms9ms', 'is_public': True})
        self._makeOne(attrib={'_id': '90k2ud90ds', 'is_public': True})
        self._makeOne(attrib={'_id': '98jd9dhydk', 'is_public': True})

        self.assertRaises(ValueError,
                          controllers.set_issue_is_public_bulk, [], is_public=False)

        ids = ['0ow9sms9ms', '90k2ud90ds', '98jd9dhydk']

        issues = controllers.get_issues_by_iid(ids)

        for issue in issues.itervalues():
            self.assertTrue(issue.is_public)


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

    def test_get_article_by_aid(self):
        """
        Teste da função controllers.get_article_by_aid para retornar um objeto:
        ``Article``.
        """

        article = self._makeOne()

        self.assertEqual(controllers.get_article_by_aid(article.id).id,
                         article.id)

    def test_get_article_by_aid_without_aid(self):
        """
        Teste da função controllers.get_article_by_aid com uma lista vazia,
        deve retorna um exceção ValueError.
        """

        self.assertRaises(ValueError, controllers.get_article_by_aid, [])

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

        self.assertEqual(articles, {})

    def test_get_articles_by_aid_without_article(self):
        """
        Testando controllers.get_articles_by_aid() sem article, deve retornar
        None.
        """

        articles = controllers.get_articles_by_aid(['aid1', 'aid12', 'aid123'])

        self.assertEqual(articles, {})

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

    def test_set_article_is_public_bulk_without_aids(self):
        """
        Testando alterar o valor de um conjunto de journals sem iids, deve
        retorna um ValueError.
        """

        self._makeOne(attrib={'_id': '9ms9kos9js', 'is_public': True})
        self._makeOne(attrib={'_id': 'lksnsh8snk', 'is_public': True})
        self._makeOne(attrib={'_id': '7153gj6ysb', 'is_public': True})

        self.assertRaises(ValueError,
                          controllers.set_article_is_public_bulk, [], is_public=False)

        ids = ['9ms9kos9js', 'lksnsh8snk', '7153gj6ysb']

        articles = controllers.get_articles_by_aid(ids)

        for article in articles.itervalues():
            self.assertTrue(article.is_public)

    def test_get_articles_by_iid(self):
        """
        Testando a função controllers.get_articles_by_iid(), deve retorna uma
        lista de articles.
        """

        self._makeOne(attrib={'_id': '012ijs9y24', 'issue': '90210j83',
                              'journal': 'oak,ajimn1'})
        self._makeOne(attrib={'_id': '2183ikos90', 'issue': '90210j83',
                              'journal': 'oak,ajimn1'})
        self._makeOne(attrib={'_id': '9298wjso89', 'issue': '90210j82',
                              'journal': 'oak,ajimn1'})

        expected = [u'012ijs9y24', u'2183ikos90']

        articles = [article.id for article in controllers.get_articles_by_iid('90210j83')]

        self.assertListEqual(sorted(articles), sorted(expected))

    def test_get_articles_by_iid_without_iid(self):
        """
        Testando a função controllers.get_articles_by_iid(), sem param iid deve
        retorna um ValueError.
        """
        self.assertRaises(ValueError,
                          controllers.get_articles_by_iid, [])


class UserControllerTestCase(BaseTestCase):

    def setUp(self):
        dbsql.create_all()

    def tearDown(self):
        dbsql.session.remove()
        dbsql.drop_all()

    def test_get_user_by_email(self):
        """
        Testando a função controllers.get_user_by_email(), deve retornar um
        usuários com o mesmo email do usuário cadastrado.
        """
        ut.create_user('xxx@yyyy.com', 'oaj9u2', True)

        user = controllers.get_user_by_email('xxx@yyyy.com')

        self.assertEqual(user.email, 'xxx@yyyy.com')

    def test_get_user_by_email_with_param_email_not_string(self):
        """
        Testando a função controllers.get_user_by_email() com o param email como
        inteiro, deve retornar um ValueError.
        """

        self.assertRaises(ValueError, controllers.get_user_by_email, 123)

    def test_get_user_by_id(self):
        """
        Testando a função controllers.get_user_by_id(), deve retornar um
        usuários com o mesmo email do usuário cadastrado.
        """
        new_user = ut.create_user('xxx@yyyy.com', 'oaj9u2', True)

        returned_user = controllers.get_user_by_id(new_user.id)

        self.assertEqual(new_user.email, returned_user.email)

    def test_get_user_by_email_with_param_id_not_string(self):
        """
        Testando a função controllers.get_user_by_id() com o param id como
        string, deve retornar um ValueError.
        """

        self.assertRaises(ValueError, controllers.get_user_by_id, 'blaus')

    def test_set_user_email_confirmed(self):
        """
        Testando a função controllers.set_user_email_confirmed().
        """
        user = ut.create_user('oamsonm@lkakjs.com', '0akdnids', False)

        controllers.set_user_email_confirmed(user)

        modified_user = controllers.get_user_by_id(user.id)

        self.assertTrue(modified_user.email_confirmed)

    def test_set_user_email_confirmed_with_param_not_user(self):
        """
        Testando a função controllers.set_user_email_confirmed() com o param
        user como string, deve retornar um ValueError.
        """

        self.assertRaises(ValueError, controllers.set_user_email_confirmed,
                          'AnotherObject')

    def test_set_user_password(self):
        """
        Testando a função controllers.set_user_password().
        """
        user = ut.create_user('oamsonm@lkakjs.com', '', True)

        controllers.set_user_password(user, '123')

        modified_user = controllers.get_user_by_id(user.id)

        self.assertTrue(check_password_hash(modified_user.password, '123'))

    def test_set_user_password_with_param_not_user(self):
        """
        Testando a função controllers.set_user_password() com o param
        user como string, deve retornar um ValueError.
        """

        self.assertRaises(ValueError, controllers.set_user_password,
                          'AnotherObject', '123')


class FunctionsInControllerTestCase(BaseTestCase):

    def test_get_current_collection(self):
        collection = utils.makeOneCollection()
        controller_col = controllers.get_current_collection()
        self.assertEqual(collection, controller_col)

    def test_count_elements_by_type_and_visibility_type_journal(self):
        """
        Testando a função count_elements_by_type_and_visibility() com 20
        periódicos cadastrados, deve retornar apenas 20 periódicos.
        """

        utils.makeAnyJournal(items=20)

        total_journal = controllers.count_elements_by_type_and_visibility('journal')

        self.assertEqual(total_journal, 20)

    def test_count_elements_by_type_and_visibility_type_issue(self):
        """
        Testando a função count_elements_by_type_and_visibility() com 20
        fascículos cadastrados, deve retornar apenas 20 fascículos.
        """

        utils.makeAnyIssue(items=20)

        total_issue = controllers.count_elements_by_type_and_visibility('issue')

        self.assertEqual(total_issue, 20)

    def test_count_elements_by_type_and_visibility_type_article(self):
        """
        Testando a função count_elements_by_type_and_visibility() com 20
        artigos cadastrados, deve retornar apenas 20 artigos.
        """

        utils.makeAnyArticle(items=20)

        total_article = controllers.count_elements_by_type_and_visibility('article')

        self.assertEqual(total_article, 20)

    def test_count_elements_by_type_and_visibility_journal_public_only(self):
        """
        Testando a função count_elements_by_type_and_visibility() com 20
        periódicos cadastrados com atributo puclic=true e 6 public=false,
        deve retornar apenas 20 periódicos(somente os periódicos marcados como
        publicos).
        """

        utils.makeAnyJournal(items=20)
        utils.makeOneJournal({'is_public': False})
        utils.makeOneJournal({'is_public': False})
        utils.makeOneJournal({'is_public': False})
        utils.makeOneJournal({'is_public': False})
        utils.makeOneJournal({'is_public': False})
        utils.makeOneJournal({'is_public': False})

        total_journal = controllers.count_elements_by_type_and_visibility('journal', public_only=True)

        self.assertEqual(total_journal, 20)

    def test_count_elements_by_type_and_visibility_issue_public_only(self):
        """
        Testando a função count_elements_by_type_and_visibility() com 50
        fascículos cadastrados com atributo puclic=true e 6 public=false,
        deve retornar apenas 20 fascículo(somente os fascículos marcados como
        publicos).
        """

        utils.makeAnyIssue(items=50)
        utils.makeOneIssue({'is_public': False})
        utils.makeOneIssue({'is_public': False})
        utils.makeOneIssue({'is_public': False})
        utils.makeOneIssue({'is_public': False})
        utils.makeOneIssue({'is_public': False})
        utils.makeOneIssue({'is_public': False})

        total_issue = controllers.count_elements_by_type_and_visibility('issue', public_only=True)

        self.assertEqual(total_issue, 50)

    def test_count_elements_by_type_and_visibility_article_public_only(self):
        """
        Testando a função count_elements_by_type_and_visibility() com 98
        artigos cadastrados com atributo puclic=true e 6 public=false,
        deve retornar apenas 20 artigo(somente os artigos marcados como
        publicos).
        """

        utils.makeAnyArticle(items=98)
        utils.makeOneArticle({'is_public': False})
        utils.makeOneArticle({'is_public': False})
        utils.makeOneArticle({'is_public': False})
        utils.makeOneArticle({'is_public': False})
        utils.makeOneArticle({'is_public': False})
        utils.makeOneArticle({'is_public': False})

        total_article = controllers.count_elements_by_type_and_visibility('article', public_only=True)

        self.assertEqual(total_article, 98)

    def test_count_elements_by_type_and_visibility_wrong_param_type(self):
        """
        Testando a função count_elements_by_type_and_visibility() com um termo
        desconhecido, deve retornar um ValueError
        """

        self.assertRaises(
            ValueError,
            controllers.count_elements_by_type_and_visibility,
            'ksjkadjkajsdkja')
