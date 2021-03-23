# coding: utf-8
from unittest.mock import patch

from werkzeug.security import check_password_hash

from .base import BaseTestCase

from webapp import controllers, dbsql, utils as ut

from flask_babelex import lazy_gettext as __

from . import utils


class JournalControllerTestCase(BaseTestCase):

    def _make_one(self, attrib=None):
        """
        Retorna um objeto ``Journal`` com os atributos obrigatórios:
        ``_id``, ``jid``, ``is_public``, o param ``attrib`` atualiza os
        atributos do objeto.
        """
        return utils.makeOneJournal(attrib=attrib)

    def _make_any(self, items=3):
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
        journal = self._make_one()
        self.assertEqual(controllers.get_journals()[0], journal)

    def test_get_public_journal(self):
        """
        Teste da função controllers.get_journals() para retorna um objeto:
        ``Journal`` explicitanto o artibuto is_public=True.
        """
        journal = self._make_one()
        self.assertEqual(controllers.get_journals(is_public=True)[0], journal)

    def test_get_not_public_journal(self):
        """
        Teste da função controllers.get_journals() para retorna um objeto:
        ``Journal`` explicitanto o artibuto is_public=False.
        """
        journal = self._make_one({'is_public': False})
        self.assertEqual(controllers.get_journals(is_public=False)[0], journal)

    def test_get_journal_order_by_acronym(self):
        """
        Teste da função controllers.get_journals() para retorna um objeto:
        ``Journal`` considerando a ordenação por acrônimo.
        """
        journal3 = self._make_one({'acronym': 'revistaC'})
        journal1 = self._make_one({'acronym': 'revistaA'})
        journal2 = self._make_one({'acronym': 'revistaB'})

        self.assertListEqual(
            [journal for journal in controllers.get_journals(order_by='acronym')],
            [journal1, journal2, journal3])

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

        journal1 = self._make_one({
            "study_areas": ["Health Sciences"],
            "last_issue": {"volume": "1", "number": "1", "year": "2016"}
        })
        journal2 = self._make_one({
            "study_areas": ["Health Sciences", "Biological Sciences"],
            "last_issue": {"volume": "2", "number": "2", "year": "2016"}
        })
        journal3 = self._make_one({
            "study_areas": ["Exact and Earth Sciences"],
            "last_issue": {"volume": "3", "number": "3", "year": "2016"}
        })
        journal4 = self._make_one({
            "study_areas": ["Human Sciences", "Biological Sciences", "Engineering"],
            "last_issue": {"volume": "4", "number": "4", "year": "2016"}
        })
        journal5 = self._make_one({
            "study_areas": ["Linguistics"],
            "last_issue": {"volume": "5", "number": "5", "year": "2016"}
        })
        journal6 = self._make_one({
            "study_areas": ["Engineering"],
            "last_issue": {"volume": "6", "number": "6", "year": "2016"}
        })

        expected = {
            'meta': {
                'total': 6,
                'themes_count': 6
            },
            'objects': {
                'Health Sciences': [
                    controllers.get_journal_json_data(journal1),
                    controllers.get_journal_json_data(journal2)
                ],
                'Engineering': [
                    controllers.get_journal_json_data(journal4),
                    controllers.get_journal_json_data(journal6)
                ],
                'Biological Sciences': [
                    controllers.get_journal_json_data(journal2),
                    controllers.get_journal_json_data(journal4)
                ],
                'Linguistics': [
                    controllers.get_journal_json_data(journal5)
                ],
                'Human Sciences': [
                    controllers.get_journal_json_data(journal4)
                ],
                'Exact and Earth Sciences': [
                    controllers.get_journal_json_data(journal3)
                ]
            }
        }

        grouped_objects = controllers.get_journals_grouped_by('study_areas')

        self.assertEqual(expected['meta']['total'], grouped_objects['meta']['total'])
        self.assertEqual(expected['meta']['themes_count'], grouped_objects['meta']['themes_count'])
        self.assertEqual(len(expected['objects']), len(grouped_objects['objects']))

        for grouper, journals in expected['objects'].items():
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

        journal1 = self._make_one({
            "index_at": ["SCIE"],
            "last_issue": {"volume": "1", "number": "1", "year": "2016"}
        })
        journal2 = self._make_one({
            "index_at": ["SCIE", "SSCI"],
            "last_issue": {"volume": "2", "number": "2", "year": "2016"}
        })
        journal3 = self._make_one({
            "index_at": ["SCIE"],
            "last_issue": {"volume": "3", "number": "3", "year": "2016"}
        })
        journal4 = self._make_one({
            "index_at": ["SSCI", "ICSE"],
            "last_issue": {"volume": "4", "number": "4", "year": "2016"}
        })
        journal5 = self._make_one({
            "index_at": ["SSCI", "SCIE"],
            "last_issue": {"volume": "5", "number": "5", "year": "2016"}
        })
        self._make_one({
            "index_at": ["SSCI"],
            "last_issue": {"volume": "6", "number": "6", "year": "2016"}
        })

        expected = {
            'meta': {
                'total': 6,
                'themes_count': 3
            },
            'objects': {
                'SCIE': [
                    controllers.get_journal_json_data(journal1),
                    controllers.get_journal_json_data(journal2),
                    controllers.get_journal_json_data(journal3),
                    controllers.get_journal_json_data(journal5)
                ],
                'SSCI': [
                    controllers.get_journal_json_data(journal2),
                    controllers.get_journal_json_data(journal4),
                    controllers.get_journal_json_data(journal5)
                ],
                'ICSE': [
                    controllers.get_journal_json_data(journal4)
                ]
            }
        }

        grouped_objects = controllers.get_journals_grouped_by('index_at')

        self.assertEqual(expected['meta']['total'], grouped_objects['meta']['total'])
        self.assertEqual(expected['meta']['themes_count'], grouped_objects['meta']['themes_count'])
        self.assertEqual(len(expected['objects']), len(grouped_objects['objects']))
        for grouper, journals in expected['objects'].items():
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

        journal1 = self._make_one({
            "publisher_name": "CNPQ",
            "last_issue": {"volume": "1", "number": "1", "year": "2016"}
        })
        journal2 = self._make_one({
            "publisher_name": "SciELO",
            "last_issue": {"volume": "2", "number": "2", "year": "2016"}
        })
        journal3 = self._make_one({
            "publisher_name": "FAPESP",
            "last_issue": {"volume": "3", "number": "3", "year": "2016"}
        })
        journal4 = self._make_one({
            "publisher_name": "FUNDAÇÃO XPTO",
            "last_issue": {"volume": "4", "number": "4", "year": "2016"}
        })
        journal5 = self._make_one({
            "publisher_name": "FAPESP",
            "last_issue": {"volume": "5", "number": "5", "year": "2016"}
        })
        journal6 = self._make_one({
            "publisher_name": "FUNDAÇÃO XPTO",
            "last_issue": {"volume": "6", "number": "6", "year": "2016"}
        })

        expected = {
            'meta': {
                'total': 6,
                'themes_count': 4
            },
            'objects': {
                'CNPQ': [
                    controllers.get_journal_json_data(journal1)
                ],
                'SciELO': [
                    controllers.get_journal_json_data(journal2),
                    controllers.get_journal_json_data(journal3),
                    controllers.get_journal_json_data(journal4),
                    controllers.get_journal_json_data(journal5)
                ],
                'FAPESP': [
                    controllers.get_journal_json_data(journal4)
                ],
                'FUNDAÇÃO XPTO': [
                    controllers.get_journal_json_data(journal4),
                    controllers.get_journal_json_data(journal6)
                ]
            }
        }

        grouped_objects = controllers.get_journals_grouped_by('publisher_name')

        self.assertEqual(expected['meta']['total'], grouped_objects['meta']['total'])
        self.assertEqual(expected['meta']['themes_count'], grouped_objects['meta']['themes_count'])
        self.assertEqual(len(expected['objects']), len(grouped_objects['objects']))

        for grouper, journals in expected['objects'].items():
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
        journal = self._make_one(attrib={'_id': 'jid123'})

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
        self._make_one(attrib={'_id': 'jid1', 'is_public': True})
        self._make_one(attrib={'_id': 'jid2', 'is_public': True})
        journal3 = self._make_one(attrib={'_id': 'jid3', 'is_public': False})
        self._make_one(attrib={'_id': 'jid4', 'is_public': False})

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

        self._make_any(items=5)

        self._make_one(attrib={'_id': 'jid1'})
        self._make_one(attrib={'_id': 'jid12'})
        self._make_one(attrib={'_id': 'jid123'})

        self._make_any(items=5)

        journals = controllers.get_journals_by_jid(['jid1', 'jid12', 'jid123'])

        expected = ['jid1', 'jid12', 'jid123']

        self.assertListEqual(sorted([journal for journal in journals.keys()]),
                             sorted(expected))

    def test_get_journals_by_jid_with_not_found_jids(self):
        """
        Testando a função controllers.get_journals_by_jid() deve retornar uma
        lista contendo objetos ``Journal`` .
        """

        self._make_any(items=5)

        self._make_one(attrib={'_id': 'jid1'})
        self._make_one(attrib={'_id': 'jid12'})
        self._make_one(attrib={'_id': 'jid123'})

        self._make_any(items=5)

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

        self._make_one(attrib={'_id': 'okls9slqwj', 'is_public': True})
        self._make_one(attrib={'_id': 'kaomkwisdp', 'is_public': True})
        self._make_one(attrib={'_id': '0wklwmnsiu', 'is_public': True})

        controllers.set_journal_is_public_bulk(
            ['okls9slqwj', 'kaomkwisdp', '0wklwmnsiu'], is_public=False)

        ids = ['okls9slqwj', 'kaomkwisdp', '0wklwmnsiu']

        journals = controllers.get_journals_by_jid(ids)

        for journal in journals.values():
            self.assertFalse(journal.is_public)

    def test_set_journal_is_public_bulk_without_jids(self):
        """
        Testando alterar o valor de um conjunto de journals, sem ids.
        """

        self._make_one(attrib={'_id': 'okls9slqwj', 'is_public': True})
        self._make_one(attrib={'_id': 'kaomkwisdp', 'is_public': True})
        self._make_one(attrib={'_id': '0wklwmnsiu', 'is_public': True})

        self.assertRaises(ValueError,
                          controllers.set_journal_is_public_bulk, [], is_public=False)

        ids = ['okls9slqwj', 'kaomkwisdp', '0wklwmnsiu']

        journals = controllers.get_journals_by_jid(ids)

        for journal in journals.values():
            self.assertTrue(journal.is_public)

    def test_get_journal_metrics_no_issn_found(self):
        journal = self._make_one({"eletronic_issn": "0101-XXXX", "print_issn" : "0101-0202"})
        self.assertEqual(
            controllers.get_journal_metrics(journal),
            {
                "total_h5_index" : 0,
                "total_h5_median" : 0,
                "h5_metric_year" : 0
            },
        )

    def test_get_journal_metrics_electronic_issn(self):
        journal = self._make_one({"eletronic_issn": "0101-XXXX", "print_issn" : "0101-0202"})
        self.assertEqual(
            controllers.get_journal_metrics(journal),
            {
                "total_h5_index" : 0,
                "total_h5_median" : 0,
                "h5_metric_year" : 0
            },
        )

    def test_get_journal_metrics_print_issn(self):
        journal = self._make_one({"print_issn" : "0101-0202"})
        self.assertEqual(
            controllers.get_journal_metrics(journal),
            {
                "total_h5_index" : 0,
                "total_h5_median" : 0,
                "h5_metric_year" : 0
            },
        )

    @patch("webapp.controllers.h5m5.get_current_metrics")
    def test_get_journal_metrics_returns_int_metrics_and_year(self, mk_get_current_metrics):
        mk_get_current_metrics.return_value = {
            "h5": "58",
            "m5": "42",
            "url": "https://scholar.google.com/citations?view_op=list_hcore&venue=xxxxxxxxxxxx.2020&hl=pt-BR",
            "year": "2020"
        }
        journal = self._make_one(
            {"eletronic_issn": "1518-8787", "print_issn" : "0034-8910"}
        )
        self.assertEqual(
            controllers.get_journal_metrics(journal),
            {
                "total_h5_index" : 58,
                "total_h5_median" : 42,
                "h5_metric_year" : 2020
            },
        )


class IssueControllerTestCase(BaseTestCase):

    def _make_one(self, attrib=None):
        """
        Retorna um objeto ``Issue`` com os atributos obrigatórios:
        ``_id``, ``jid``, ``is_public`` e ``journal``, o param ``attrib`` atualiza os
        atributos do objeto.
        """
        return utils.makeOneIssue(attrib=attrib)

    def _make_any(self, journal=None, items=3):
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

        issue = self._make_one()

        self.assertEqual(controllers.get_issues_by_jid(issue.journal.id)[0].id,
                         issue.id)

    def test_get_issues_by_jid_with_many_items(self):
        """
        Teste da função controllers.get_issue_by_jid() com vários itens, deve
        deve retorna uma lista.
        """

        journal = utils.makeOneJournal()

        self._make_one({'_id': '1', 'journal': journal.id})
        self._make_one({'_id': '2', 'journal': journal.id})
        self._make_one({'_id': '3', 'journal': journal.id})
        self._make_one({'_id': '4', 'journal': journal.id})

        issues = [issue.id for issue in controllers.get_issues_by_jid(journal.id)]

        self.assertListEqual(sorted(issues), sorted(['1', '2', '3', '4']))

    def test_get_issues_by_jid_changing_default_order_by(self):
        """
        Teste da função controllers.get_issue_by_jid() com vários itens, deve
        deve retorna uma lista considerando o valor explicito do atributo
        ``order_by``
        """

        journal = utils.makeOneJournal()

        self._make_one({'_id': '1', 'journal': journal.id, 'number': '10'})
        self._make_one({'_id': '2', 'journal': journal.id, 'number': '9'})
        self._make_one({'_id': '3', 'journal': journal.id, 'number': '8'})
        self._make_one({'_id': '4', 'journal': journal.id, 'number': '7'})

        issues = [issue.id for issue in controllers.get_issues_by_jid(journal.id, order_by=['number'])]

        self.assertListEqual(sorted(issues), sorted(['4', '3', '2', '1']))

    def test_get_issues_by_jid_with_unknow_ids(self):
        """
        Teste da função controllers.get_issue_by_jid() com um jid desconhecido,
        deve retornar um None.
        """

        issues = controllers.get_issues_by_jid('02i28wjs92u')

        self.assertEqual([], list(issues))

    def test_get_issue_by_journal_and_assets_code_raises_error_if_no_assets_code(self):
        """
        Teste da função controllers.get_issue_by_journal_and_issue_info() com assets_code
        vazio lança exceção.
        """
        journal = utils.makeOneJournal()
        with self.assertRaises(ValueError) as exc_info:
            controllers.get_issue_by_journal_and_assets_code('', journal)
        self.assertEqual(str(exc_info.exception), __('Obrigatório um assets_code.'))

    def test_get_issue_by_journal_and_assets_code_raises_error_if_no_journal(self):
        """
        Teste da função controllers.get_issue_by_journal_and_issue_info() com journal
        vazio lança exceção.
        """
        with self.assertRaises(ValueError) as exc_info:
            controllers.get_issue_by_journal_and_assets_code('v1n1', {})
        self.assertEqual(str(exc_info.exception), __('Obrigatório um journal.'))

    @patch('webapp.controllers.Issue.objects')
    def test_get_issue_by_journal_and_assets_code_returns_filter_first_result(
        self, mk_issue_objects
    ):
        """
        Teste da função controllers.get_issue_by_journal_and_issue_info() com issue não
        encontrado com o assets_code e journal informado.
        """
        journal = utils.makeOneJournal()
        issue = utils.makeOneIssue()
        mk_issue_objects.filter.return_value.first.return_value = issue
        result = controllers.get_issue_by_journal_and_assets_code('v1n1', journal)
        self.assertEqual(result, issue)

    def test_get_issue_by_iid(self):
        """
        Teste da função controllers.get_issue_by_iid() para retornar um objeto:
        ``Issue``.
        """
        issue = self._make_one()
        self.assertEqual(controllers.get_issue_by_iid(issue.id), issue)

    def test_get_issue_by_label(self):
        """
        Teste da função controllers.get_issue_by_label() para retornar um objeto:
        ``Issue``.
        """
        issue = self._make_one()
        self.assertEqual(controllers.get_issue_by_label(issue.journal, issue.label), issue)

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
        issue = self._make_one({'volume': '10', 'number': '4'})

        self._make_any(items=30)

        self.assertEqual(controllers.get_issue_by_iid(issue.id, volume='10',
                         number='4'), issue)

    def test_get_issues_by_iid(self):
        """
        Testando a função controllers.get_issues_by_iid() deve retornar uma
        lista contendo objetos ``Issue``.
        """

        self._make_any(items=5)

        self._make_one(attrib={'_id': 'iid1'})
        self._make_one(attrib={'_id': 'iid12'})
        self._make_one(attrib={'_id': 'iid123'})

        self._make_any(items=5)

        issues = controllers.get_issues_by_iid(['iid1', 'iid12', 'iid123'])

        expected = ['iid1', 'iid12', 'iid123']

        self.assertListEqual(sorted([issue for issue in issues.keys()]),
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

        self._make_one(attrib={'_id': '012ijs9y24', 'is_public': True})
        self._make_one(attrib={'_id': '2183ikos90', 'is_public': True})
        self._make_one(attrib={'_id': '9298wjso89', 'is_public': True})

        controllers.set_issue_is_public_bulk(
            ['012ijs9y24', '2183ikos90', '9298wjso89'], is_public=False)

        ids = ['012ijs9y24', '2183ikos90', '9298wjso89']

        issues = controllers.get_issues_by_iid(ids)

        for issue in issues.values():
            self.assertFalse(issue.is_public)

    def test_set_issue_is_public_bulk_setting_reason(self):
        """
        Testando alterar o valor de um conjunto de issues com o motivo, param
        ``reason``.
        """
        unpublish_reason = 'plágio'
        self._make_one(attrib={'_id': '012ijs9y24', 'is_public': True})
        self._make_one(attrib={'_id': '2183ikos90', 'is_public': True})
        self._make_one(attrib={'_id': '9298wjso89', 'is_public': True})

        ids = ['012ijs9y24', '2183ikos90', '9298wjso89']

        controllers.set_issue_is_public_bulk(ids, is_public=False,
                                             reason='plágio')

        issues = controllers.get_issues_by_iid(ids)

        for issue in issues.values():
            self.assertEqual(unpublish_reason, issue.unpublish_reason)

    def test_set_issue_is_public_bulk_without_iids(self):
        """
        Testando alterar o valor de um conjunto de journals, sem ids.
        """

        self._make_one(attrib={'_id': '0ow9sms9ms', 'is_public': True})
        self._make_one(attrib={'_id': '90k2ud90ds', 'is_public': True})
        self._make_one(attrib={'_id': '98jd9dhydk', 'is_public': True})

        self.assertRaises(ValueError,
                          controllers.set_issue_is_public_bulk, [], is_public=False)

        ids = ['0ow9sms9ms', '90k2ud90ds', '98jd9dhydk']

        issues = controllers.get_issues_by_iid(ids)

        for issue in issues.values():
            self.assertTrue(issue.is_public)


class ArticleControllerTestCase(BaseTestCase):

    def _make_one(self, attrib=None):
        """
        Retorna um objeto ``Article`` com os atributos obrigatórios:
        ``_id``, ``jid``, ``is_public`` e ``issue`` o param ``attrib`` atualiza
        os atributos do objeto.
        """
        return utils.makeOneArticle(attrib=attrib)

    def _make_any(self, issue=None, items=3):
        """
        Retorna uma lista de objetos ``Article`` com atributos ``jid``,
        ``is_public`` e ``acronym`` limitando a quantidade pelo param ``items``.
        """
        return utils.makeAnyArticle(issue=issue, items=items)

    def _make_same_issue_articles(self, articles_attribs=None):
        issue = utils.makeOneIssue()
        default_attribs = [
            {
                "original_language": "pt",
                "languages": ["pt", ],
                "abstracts": [{"language": "pt", "text": ""}],
                "abstract_languages": ["pt"],
            },
            {
                "original_language": "es",
                "languages": ["es", ],
                "abstracts": [{"language": "es", "text": ""}],
                "abstract_languages": ["es"],
            },
        ]
        articles_attribs = articles_attribs or default_attribs
        articles = []
        for article_attribs in articles_attribs:
            article_attribs.update({"issue": issue})
            articles.append(self._make_one(article_attribs))
        return articles

    def test_get_article_returns_next_article(self):
        """
        Teste da função controllers.get_article para retornar um objeto:
        ``Article``.
        """
        articles = self._make_same_issue_articles()
        article = articles[1]
        lang, result = controllers.get_article(
            articles[0].id,
            articles[0].journal.url_segment,
            articles[0].original_language,
            gs_abstract=False,
            goto="next",
        )
        self.assertEqual(article.id, result.id)
        self.assertEqual(lang, "es")

    def test_get_article_returns_previous_article(self):
        """
        Teste da função controllers.get_article para retornar um objeto:
        ``Article``.
        """
        articles = self._make_same_issue_articles()
        article = articles[0]
        lang, result = controllers.get_article(
            articles[1].id,
            articles[1].journal.url_segment,
            articles[1].original_language,
            gs_abstract=False,
            goto="previous",
        )
        self.assertEqual(article.id, result.id)
        self.assertEqual(lang, "pt")

    def test_get_article_returns_article(self):
        """
        Teste da função controllers.get_article para retornar um objeto:
        ``Article``.
        """
        articles = self._make_same_issue_articles()
        article = articles[0]
        lang, result = controllers.get_article(
            articles[0].id,
            articles[0].journal.url_segment,
            "pt",
            gs_abstract=False,
        )
        self.assertEqual(article.id, result.id)
        self.assertEqual(lang, "pt")

    def test_get_article_returns_article_and_original_lang(self):
        """
        Teste da função controllers.get_article para retornar um objeto:
        ``Article``.
        """
        articles = self._make_same_issue_articles()
        article = articles[0]
        lang, result = controllers.get_article(
            articles[0].id,
            articles[0].journal.url_segment,
            None,
            gs_abstract=False,
        )
        self.assertEqual(article.id, result.id)
        self.assertEqual(lang, "pt")

    def test_get_article_returns_next_article_which_has_abstract(self):
        """
        Teste da função controllers.get_article para retornar um objeto:
        ``Article``.
        """
        articles = self._make_same_issue_articles()
        article = articles[1]
        lang, result = controllers.get_article(
            articles[0].id,
            articles[0].journal.url_segment,
            "en",
            gs_abstract=True,
            goto="next",
        )
        self.assertEqual(article.id, result.id)
        self.assertEqual(lang, "es")

    def test_get_article_returns_previous_article_which_has_abstract(self):
        """
        Teste da função controllers.get_article para retornar um objeto:
        ``Article``.
        """
        articles = self._make_same_issue_articles()
        article = articles[0]
        lang, result = controllers.get_article(
            articles[1].id,
            articles[1].journal.url_segment,
            "en",
            gs_abstract=True,
            goto="previous",
        )
        self.assertEqual(article.id, result.id)
        self.assertEqual(lang, "pt")

    def test_get_article_returns_article_which_has_abstract(self):
        """
        Teste da função controllers.get_article para retornar um objeto:
        ``Article``.
        """
        articles = self._make_same_issue_articles()
        article = articles[0]
        lang, result = controllers.get_article(
            articles[0].id,
            articles[0].journal.url_segment,
            "pt",
            gs_abstract=True,
        )
        self.assertEqual(article.id, result.id)
        self.assertEqual(lang, "pt")

    def test_goto_article_returns_next_article(self):
        articles = self._make_same_issue_articles()
        self.assertEqual(
            controllers.goto_article(articles[0], "next").id,
            articles[1].id
        )

    def test_goto_article_returns_no_next(self):
        articles = self._make_same_issue_articles()
        with self.assertRaises(controllers.ArticleNotFoundError):
            controllers.goto_article(articles[-1], "next")

    def test_goto_article_returns_previous_article(self):
        articles = self._make_same_issue_articles()
        self.assertEqual(
            controllers.goto_article(articles[-1], "previous").id,
            articles[-2].id
        )

    def test_goto_article_returns_no_previous(self):
        articles = self._make_same_issue_articles()
        with self.assertRaises(controllers.ArticleNotFoundError):
            controllers.goto_article(articles[0], "previous")

    def test_goto_article_returns_next_article_with_abstract(self):
        articles = self._make_same_issue_articles()
        self.assertEqual(
            controllers.goto_article(articles[0], "next", True).id,
            articles[1].id
        )

    def test_goto_article_returns_no_next_because_next_has_no_abstract(self):
        attribs = [
            {"abstracts": [{"language": "x", "text": ""}]},
            {},
        ]
        articles = self._make_same_issue_articles(attribs)
        with self.assertRaises(controllers.ArticleNotFoundError):
            controllers.goto_article(articles[0], "next", True)

    def test_goto_article_returns_previous_article_with_abstract(self):
        articles = self._make_same_issue_articles()
        self.assertEqual(
            controllers.goto_article(articles[-1], "previous", True).id,
            articles[-2].id
        )

    def test_goto_article_returns_no_previous_because_previous_has_no_abstract(self):
        attribs = [
            {},
            {"abstracts": [{"language": "x", "text": ""}]},
        ]
        articles = self._make_same_issue_articles(attribs)
        with self.assertRaises(controllers.ArticleNotFoundError):
            controllers.goto_article(articles[-1], "previous", True)

    def test_goto_article_returns_no_previous_because_previous_has_no_abstract(self):
        attribs = [
            {},
            {"abstracts": [{"language": "x", "text": ""}]},
        ]
        articles = self._make_same_issue_articles(attribs)
        with self.assertRaises(ValueError) as exc:
            controllers.goto_article(articles[-1], "prev", True)
        self.assertIn("Expected: next or previous", str(exc.exception))

    def test__articles_or_abstracts_sorted_by_order_or_date_returns_empty_list(self):
        abstracts = []
        a = self._make_one({"abstracts": abstracts})
        articles = controllers._articles_or_abstracts_sorted_by_order_or_date(
            a.issue.id, gs_abstract=True)
        self.assertEqual(articles, [])

    def test__articles_or_abstracts_sorted_by_order_or_date_returns_empty_list2(self):
        a = self._make_one({"abstracts": None})
        articles = controllers._articles_or_abstracts_sorted_by_order_or_date(
            a.issue.id, gs_abstract=True)
        self.assertEqual(articles, [])

    def test__articles_or_abstracts_sorted_by_order_or_date_returns_empty_list3(self):
        a = self._make_one()
        articles = controllers._articles_or_abstracts_sorted_by_order_or_date(
            a.issue.id, gs_abstract=True)
        self.assertEqual(articles, [])

    def test__articles_or_abstracts_sorted_by_order_or_date_returns_one(self):
        abstracts = [
            {"language": "en", "text": "Texto"}
        ]
        abstract_languages = ["en"]
        a = self._make_one(
            {
                "abstracts": abstracts,
                "abstract_languages": abstract_languages
            }
        )
        articles = controllers._articles_or_abstracts_sorted_by_order_or_date(
            a.issue.id, gs_abstract=True)
        self.assertEqual(len(articles), 1)

    def test_get_articles_by_aid(self):
        """
        Testando a função controllers.get_articles_by_aid() deve retornar uma
        lista contendo objetos ``Article`` .
        """

        self._make_any(items=5)

        self._make_one(attrib={'_id': 'aid1'})
        self._make_one(attrib={'_id': 'aid12'})
        self._make_one(attrib={'_id': 'aid123'})

        self._make_any(items=5)

        articles = controllers.get_articles_by_aid(['aid1', 'aid12', 'aid123'])

        expected = ['aid1', 'aid12', 'aid123']

        self.assertListEqual(sorted([article for article in articles.keys()]),
                             sorted(expected))

    def test_get_articles_by_aid_with_not_found_jids(self):
        """
        Testando a função controllers.get_articles_by_aid() deve retornar um
        None.
        """

        self._make_any(items=5)

        self._make_one(attrib={'_id': 'aid1'})
        self._make_one(attrib={'_id': 'aid12'})
        self._make_one(attrib={'_id': 'aid123'})

        self._make_any(items=5)

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

        self._make_one(attrib={'_id': '012ijs9y24', 'is_public': True})
        self._make_one(attrib={'_id': '2183ikos90', 'is_public': True})
        self._make_one(attrib={'_id': '9298wjso89', 'is_public': True})

        controllers.set_article_is_public_bulk(
            ['012ijs9y24', '2183ikos90', '9298wjso89'], is_public=False)

        ids = ['012ijs9y24', '2183ikos90', '9298wjso89']

        articles = controllers.get_articles_by_aid(ids)

        for article in articles.values():
            self.assertFalse(article.is_public)

    def test_set_article_is_public_bulk_without_aids(self):
        """
        Testando alterar o valor de um conjunto de journals sem iids, deve
        retorna um ValueError.
        """

        self._make_one(attrib={'_id': '9ms9kos9js', 'is_public': True})
        self._make_one(attrib={'_id': 'lksnsh8snk', 'is_public': True})
        self._make_one(attrib={'_id': '7153gj6ysb', 'is_public': True})

        self.assertRaises(ValueError,
                          controllers.set_article_is_public_bulk, [], is_public=False)

        ids = ['9ms9kos9js', 'lksnsh8snk', '7153gj6ysb']

        articles = controllers.get_articles_by_aid(ids)

        for article in articles.values():
            self.assertTrue(article.is_public)

    def test_get_articles_by_iid(self):
        """
        Testando a função controllers.get_articles_by_iid(), deve retorna uma
        lista de articles.
        """

        self._make_one(attrib={
            '_id': '012ijs9y24',
            'issue': '90210j83',
            'order': '14',
            'journal': 'oak,ajimn1'
        })
        self._make_one(attrib={
            '_id': '2183ikos90',
            'issue': '90210j83',
            'order': '12',
            'journal': 'oak,ajimn1'
        })
        self._make_one(attrib={
            '_id': '9298wjso89',
            'issue': '90210j82',
            'order': '13',
            'journal': 'oak,ajimn1'
        })

        expected = ['2183ikos90', '012ijs9y24', ]

        articles = [article.id for article in controllers.get_articles_by_iid('90210j83')]

        self.assertListEqual(articles, expected)

    def test_get_articles_by_iid_from_aop_issue(self):
        """
        Testando a função controllers.get_articles_by_iid(), deve retorna uma
        lista de articles.
        """
        issue = utils.makeOneIssue({"_id": '90210j83', "number": "ahead"})
        self._make_one(attrib={
            '_id': '012ijs9y24',
            'issue': issue,
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01-01',
            'is_aop': True,
        })

        self._make_one(attrib={
            '_id': '2183ikos90',
            'issue': issue,
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01-10',
            'is_aop': True,
        })

        self._make_one(attrib={
            '_id': '9298wjso89',
            'issue': issue,
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01-08',
            'is_aop': True,
        })

        expected = ['2183ikos90', '9298wjso89', '012ijs9y24']

        articles = [article.id for article in controllers.get_articles_by_iid('90210j83')]

        self.assertListEqual(articles, expected)

    def test_get_articles_by_iid_from_regular_issue_with_ex_aop(self):
        """
        Testando a função controllers.get_articles_by_iid(), deve retorna uma
        lista de articles.
        """

        self._make_one(attrib={
            '_id': '012ijs9y24',
            'issue': '90210j83',
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01-01',
            'aop_pid': 'S111',
        })

        self._make_one(attrib={
            '_id': '2183ikos90',
            'issue': '90210j83',
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01-10',
            'is_aop': True,
            'aop_pid': 'S111',
        })

        self._make_one(attrib={
            '_id': '9298wjso89',
            'issue': '90210j83',
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01-08',
            'is_aop': True,
            'aop_pid': 'S111',
        })

        expected = ['012ijs9y24', '2183ikos90', '9298wjso89', ]

        articles = [article.id for article in controllers.get_articles_by_iid('90210j83')]

        self.assertListEqual(articles, expected)

    def test_get_articles_by_iid_from_regular_issue_with_ex_aop_and_regular_articles(self):
        """
        Testando a função controllers.get_articles_by_iid(), deve retorna uma
        lista de articles.
        """

        self._make_one(attrib={
            '_id': '012ijs9y24',
            'issue': '90210j83',
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01',
        })

        self._make_one(attrib={
            '_id': '2183ikos90',
            'issue': '90210j83',
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01-10',
            'is_aop': True,
            'aop_pid': 'S111',
        })

        self._make_one(attrib={
            '_id': '9298wjso89',
            'issue': '90210j83',
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01-08',
            'is_aop': True,
            'aop_pid': 'S111',
        })

        expected = ['012ijs9y24', '2183ikos90', '9298wjso89', ]

        articles = [article.id for article in controllers.get_articles_by_iid('90210j83')]

        self.assertListEqual(articles, expected)

    def test_get_articles_by_iid_from_continuous_publication_issue(self):
        """
        Testando a função controllers.get_articles_by_iid(), deve retorna uma
        lista de articles.
        """

        self._make_one(attrib={
            '_id': '012ijs9y24',
            'issue': '90210j83',
            'elocation': "a1",
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01-01',
        })

        self._make_one(attrib={
            '_id': '2183ikos90',
            'issue': '90210j83',
            'elocation': "a2",
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01-10',
        })

        self._make_one(attrib={
            '_id': '9298wjso89',
            'issue': '90210j83',
            'elocation': "a3",
            'journal': 'oak,ajimn1',
            'publication_date': '2018-01-08',
        })

        expected = ['2183ikos90', '9298wjso89', '012ijs9y24', ]

        articles = [article.id for article in controllers.get_articles_by_iid('90210j83')]

        self.assertListEqual(articles, expected)

    def test_get_articles_by_iid_without_iid(self):
        """
        Testando a função controllers.get_articles_by_iid(), sem param iid deve
        retorna um ValueError.
        """
        self.assertRaises(ValueError, controllers.get_articles_by_iid, [])

    def test_get_article_by_scielo_pid_with_no_pid(self):
        """
        Testando a função controllers.get_article_by_scielo_pid(), sem pid
        retorna um ValueError.
        """
        self.assertRaises(ValueError, controllers.get_article_by_scielo_pid, scielo_pid="")

    def test_get_article_by_scielo_pid_returns_none_if_no_pid_in_scielo_pids(self):
        """
        Testando a função controllers.get_article_by_scielo_pid(), sem pid
        retorna um ValueError.
        """
        self._make_one(attrib={
            '_id': '012ijs9y24',
            'issue': '90210j83',
            'journal': 'oak,ajimn1',
            'scielo_pids': {
                'v1': 'S0101-0202(99)12345',
                'v2': 'S0101-02021998123456',
                'v3': 'cS2o3kdx93emd902m',
            },
        })
        self.assertIsNone(controllers.get_article_by_scielo_pid("S0101-0202(99)12344"))

    def test_get_article_by_scielo_pid_returns_article(self):
        """
        Testando a função controllers.get_article_by_scielo_pid(), retorna artigo com sucesso.
        """
        self._make_one(attrib={
            '_id': '012ijs9y24',
            'issue': '90210j83',
            'journal': 'oak,ajimn1',
            'scielo_pids': {
                'v1': 'S0101-0202(99)12345',
                'v2': 'S0101-02021998123456',
                'v3': 'cS2o3kdx93emd902m',
            },
        })
        article = controllers.get_article_by_scielo_pid("S0101-0202(99)12345")
        self.assertEqual(article._id, '012ijs9y24')
        self.assertEqual(article.scielo_pids["v1"], 'S0101-0202(99)12345')

    def test_get_recent_articles_of_issue(self):
        self._make_one(attrib={
            '_id': '012ijs9y24',
            'issue': '90210j83',
            'journal': 'oak,ajimn1'
        })

        self._make_one(attrib={
            '_id': '2183ikos90',
            'issue': '90210j83',
            'type': 'article-commentary',
            'journal': 'oak,ajimn1'
        })

        self._make_one(attrib={
            '_id': '012ijs9y14',
            'issue': '90210j83',
            'type': 'brief-report',
            'journal': 'oak,ajimn1'
        })

        self._make_one(attrib={
            '_id': '2183ikoD90',
            'issue': '90210j83',
            'type': 'case-report',
            'journal': 'oak,ajimn1'
        })

        self._make_one(attrib={
            '_id': '2183ikos9B',
            'issue': '90210j83',
            'type': 'rapid-communication',
            'journal': 'oak,ajimn1'
        })

        self._make_one(attrib={
            '_id': '012ijs9y1B',
            'issue': '90210j83',
            'type': 'research-article',
            'journal': 'oak,ajimn1'
        })

        self._make_one(attrib={
            '_id': '2183ikoD9F',
            'issue': '90210j83',
            'type': 'review-article',
            'journal': 'oak,ajimn1'
        })

        self._make_one(attrib={
            '_id': '9298wjXX89',
            'issue': '90210j83',
            'journal': 'oak,ajimn1'
        })
        self._make_one(attrib={
            '_id': '9298wjXZ89',
            'issue': '90210j83',
            'journal': 'oak,ajimn1'
        })
        result = controllers.get_recent_articles_of_issue(
            issue_iid='90210j83', is_public=True)
        self.assertEqual(len(result), 6)
        result = [article._id for article in result]
        expected = ['2183ikos90', '2183ikoD90', '2183ikos9B', '012ijs9y1B',
                    '2183ikoD9F', '012ijs9y14']
        self.assertEqual(set(result), set(expected))

    @patch('webapp.controllers.Article.objects')
    @patch('webapp.controllers.get_journal_by_acron')
    @patch('webapp.controllers.get_issue_by_label')
    def test_get_article_by_pdf_filename_retrieves_articles_by_pdf_filename(
        self, mk_get_issue_by_label, mk_get_journal_by_acron, mk_article_objects
    ):

        article = self._make_one(attrib={
                                 '_id': '012ijs9y24',
                                 'issue': '90210j83',
                                 'journal': 'oak,ajimn1'
                                 })

        mk_get_journal_by_acron.return_value = article.journal
        mk_get_issue_by_label.return_value = article.issue

        controllers.get_article_by_pdf_filename(article.journal, article.issue, "article.pdf")

        mk_article_objects.filter.assert_called_once_with(is_public=True,
                                                          issue=article.issue,
                                                          journal=article.journal,
                                                          pdfs__filename='article.pdf'
                                                          )

    def test_get_article_by_pdf_filename_raises_error_if_no_journal_acronym(self):
        with self.assertRaises(ValueError) as exc_info:
            controllers.get_article_by_pdf_filename("", "v1n3s2", "article.pdf")
        self.assertEqual(
            str(exc_info.exception), __('Obrigatório o acrônimo do periódico.')
        )

    def test_get_article_by_pdf_filename_raises_error_if_no_issue_info(self):
        with self.assertRaises(ValueError) as exc_info:
            controllers.get_article_by_pdf_filename("abc", "", "article.pdf")
        self.assertEqual(
            str(exc_info.exception), __('Obrigatório o campo issue_info.')
        )

    def test_get_article_by_pdf_filename_raises_error_if_no_pdf_filename(self):
        with self.assertRaises(ValueError) as exc_info:
            controllers.get_article_by_pdf_filename("abc", "v1n3s2", "")
        self.assertEqual(
            str(exc_info.exception), __('Obrigatório o nome do arquivo PDF.')
        )

    @patch('webapp.controllers.Article.objects')
    def test_get_article_by_pdf_filename_raises_error_if_article_filter_error(
        self, mk_article_objects
    ):
        mk_article_objects.filter.return_value.first.side_effect = Exception
        self.assertRaises(
            Exception,
            controllers.get_article_by_pdf_filename,
            "abc",
            "v1n3s2",
            "article.pdf"
        )

    def test_set_articles_full_text_unavailable(self):
        ids = ['1', '2', '3']

        for id in ids:
            self._make_one(attrib={'_id': id, 'display_full_text': True})

        controllers.set_article_display_full_text_bulk(ids, display=False)
        articles = controllers.get_articles_by_aid(ids)

        for article in articles.values():
            self.assertFalse(article.display_full_text)

    def test_set_articles_full_text_available(self):
        ids = ['1', '2', '3']

        for id in ids:
            self._make_one(attrib={'_id': id, 'display_full_text': False})

        controllers.set_article_display_full_text_bulk(ids, display=True)
        articles = controllers.get_articles_by_aid(ids)

        for article in articles.values():
            self.assertTrue(article.display_full_text)

    def test_get_article_by_aid_raises_missing_aid_parameter_error(self):
        with self.assertRaises(ValueError) as exc:
            controllers.get_article_by_aid(None, None)
        self.assertIn("aid", str(exc.exception))

    def test_get_article_by_aid_raises_article_not_found_error(self):
        with self.assertRaises(controllers.ArticleNotFoundError) as exc:
            controllers.get_article_by_aid("notid", None)
        self.assertIn("notid", str(exc.exception))

    def test_get_article_by_aid_raises_missing_journal_url_seg_parameter_error(
            self):
        article = self._make_one()
        with self.assertRaises(ValueError) as exc:
            controllers.get_article_by_aid(article.id, None)
        self.assertIn("journal_url_seg", str(exc.exception))

    def test_get_article_by_aid_raises_not_found_article_journal_error(
            self):
        article = self._make_one({'journal': 'JOURNALID02'})
        with self.assertRaises(controllers.ArticleJournalNotFoundError) as exc:
            controllers.get_article_by_aid(article.id, "JOURNALID01")
        self.assertIn(article.journal.acronym, str(exc.exception))

    def test_get_article_by_aid_raises_article_is_not_published_error(
            self):
        article = self._make_one({"is_public": False})
        with self.assertRaises(controllers.ArticleIsNotPublishedError):
            controllers.get_article_by_aid(
                article.id, article.journal.url_segment)

    def test_get_article_by_aid_raises_issue_is_not_published_error(
            self):
        issue = utils.makeOneIssue({"is_public": False})
        article = self._make_one({"issue": issue})

        with self.assertRaises(controllers.IssueIsNotPublishedError):
            controllers.get_article_by_aid(
                article.id, article.journal.url_segment)

    def test_get_article_by_aid_raises_journal_is_not_published_error(
            self):
        journal = utils.makeOneJournal({"is_public": False})
        article = self._make_one({"journal": journal})
        with self.assertRaises(controllers.JournalIsNotPublishedError):
            controllers.get_article_by_aid(
                article.id, article.journal.url_segment)

    def test_get_article_by_aid_raises_article_lang_not_found_error(
            self):
        article = self._make_one()
        with self.assertRaises(controllers.ArticleLangNotFoundError) as exc:
            controllers.get_article_by_aid(
                article.id, article.journal.url_segment, "xx")
        self.assertEqual(
            str([article.original_language] + article.languages),
            str(exc.exception)
        )

    def test_get_article_by_aid_raises_article_abstract_not_found_error(
            self):
        article = self._make_one()
        with self.assertRaises(controllers.ArticleAbstractNotFoundError) as exc:
            controllers.get_article_by_aid(
                article.id, article.journal.url_segment, "zz", True)
        self.assertEqual(
            str(article.abstract_languages),
            str(exc.exception)
        )

    def test_get_article_by_aid_returns_article(self):
        """
        Teste da função controllers.get_article_by_aid para retornar um objeto:
        ``Article``.
        """

        article = self._make_one()
        id, url_seg = article.id, article.journal.url_segment
        self.assertEqual(
            controllers.get_article_by_aid(id, url_seg).id,
            article.id
        )



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

        self.assertRaises(ValueError, controllers.set_user_email_confirmed, 'AnotherObject')

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

    def test_get_current_collection_get_public_and_current_journals_numbers(self):
        collection = utils.makeOneCollection({
            "metrics" : {
                "total_journal" : 10,
                "total_issue" : 2000,
                "total_article" : 30000,
                "total_citation" : 400000
            },
        })
        utils.makeAnyJournal(
            items=20, attrib={'is_public': True, 'current_status': 'current'}
        )
        utils.makeOneJournal({'is_public': False, 'current_status': 'current'})
        utils.makeOneJournal({'is_public': False, 'current_status': 'current'})
        utils.makeOneJournal({'is_public': False, 'current_status': 'current'})
        utils.makeOneJournal({'current_status': 'deceased'})
        utils.makeOneJournal({'current_status': 'deceased'})
        utils.makeOneJournal({'current_status': 'deceased'})
        utils.makeOneJournal({'current_status': 'suspended'})
        controller_col = controllers.get_current_collection()
        self.assertEqual(controller_col.metrics.total_journal, 20)

    def test_get_current_collection_get_public_issues_numbers(self):
        collection = utils.makeOneCollection({
            "metrics" : {
                "total_journal" : 10,
                "total_issue" : 2000,
                "total_article" : 30000,
                "total_citation" : 400000
            },
        })
        utils.makeAnyIssue(items=50, attrib={'is_public': True})
        utils.makeOneIssue({'is_public': False})
        utils.makeOneIssue({'is_public': False})
        utils.makeOneIssue({'is_public': False})
        utils.makeOneIssue({'is_public': False})
        controller_col = controllers.get_current_collection()
        self.assertEqual(controller_col.metrics.total_issue, 50)

    def test_get_current_collection_get_public_articles_numbers(self):
        collection = utils.makeOneCollection({
            "metrics" : {
                "total_journal" : 10,
                "total_issue" : 2000,
                "total_article" : 30000,
                "total_citation" : 400000
            },
        })
        utils.makeAnyArticle(items=101, attrib={'is_public': True})
        utils.makeOneArticle({'is_public': False})
        utils.makeOneArticle({'is_public': False})
        utils.makeOneArticle({'is_public': False})
        utils.makeOneArticle({'is_public': False})
        controller_col = controllers.get_current_collection()
        self.assertEqual(controller_col.metrics.total_article, 101)

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
        números cadastrados, deve retornar apenas 20 números.
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
        números cadastrados com atributo puclic=true e 6 public=false,
        deve retornar apenas 20 números (somente os números marcados como
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


class PageControllerTestCase(BaseTestCase):

    def _make_one(self, attrib=None):
        """
        Retorna um objeto ``Pages`` com os atributos obrigatórios:
        ``_id``, o param ``attrib`` atualiza os atributos do objeto.
        """
        return utils.makeOnePage(attrib=attrib)

    def test_get_page_by_lang(self):
        """
        Teste da função controllers.get_pages_by_lang() para retornar um objeto:
        ``Pages``.
        """
        page = self._make_one()
        self.assertEqual(
            [page.language for page in controllers.get_pages()],
            [page['language']])
        self.assertEqual(
            [page.language for page in controllers.get_pages_by_lang(
                lang='pt_BR')],
            ['pt_BR'])

    def test_get_page_by_slug_name(self):
        """
        Teste da função controllers.get_page_by_slug_name()
        para retornar um objeto: ``Pages``.
        """
        page = self._make_one({'name': 'Critérios', 'language': 'pt_BR', 'content': 'texto em port.'})
        page = self._make_one({'name': 'Criterios', 'language': 'es_ES', 'content': 'texto en esp.'})
        slug_name = page.slug_name

        _page = controllers.get_page_by_slug_name(slug_name, 'es_ES')
        self.assertEqual('Criterios', _page.name)
        self.assertEqual('texto en esp.', _page.content)
        self.assertEqual('es_ES', _page.language)

        _page = controllers.get_page_by_slug_name(slug_name, 'pt_BR')
        self.assertEqual('Critérios', _page.name)
        self.assertEqual('pt_BR', _page.language)
        self.assertEqual('texto em port.', _page.content)

        _page = controllers.get_page_by_slug_name(slug_name, 'en_US')
        self.assertIsNone(_page)

        _page = controllers.get_page_by_slug_name('Bla')
        self.assertEqual(len(_page), 0)

        _page = controllers.get_page_by_slug_name(slug_name)
        self.assertEqual(len(_page), 2)
        self.assertEqual(
            {item.name for item in _page},
            {'Critérios', 'Criterios'}
            )

