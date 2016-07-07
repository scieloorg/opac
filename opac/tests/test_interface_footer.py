# coding: utf-8

from flask import url_for, current_app
from base import BaseTestCase

import utils


class FooterTestCase(BaseTestCase):

    def test_collection_open_access_home(self):
        """
        Testa se os links e o conteúdo da licença esta de acordo com a licença
        cadastrada na coleção.
        """

        with current_app.app_context():
            collection = utils.makeOneCollection()

            with self.client as c:

                response = c.get(url_for('main.index'))

                self.assertStatus(response, 200)

                self.assertTemplateUsed('collection/index.html')

                self.assertIn('/static/img/oa_logo_32.png', response.data)
                self.assertIn('href="%s"' % url_for('main.open_access'), response.data)
                self.assertIn('Open Access', response.data)

    def test_collection_open_access_list_theme(self):
        """
        Testa se os links e o conteúdo da licença esta de acordo com a licença
        cadastrada na coleção.
        """
        with current_app.app_context():
            collection = utils.makeOneCollection()

            with self.client as c:

                response = c.get(url_for('main.collection_list_theme'))

                self.assertStatus(response, 200)

                self.assertTemplateUsed('collection/list_theme.html')

                self.assertIn('/static/img/oa_logo_32.png', response.data)
                self.assertIn('href="%s"' % url_for('main.open_access'), response.data)
                self.assertIn('Open Access', response.data)

    def test_collection_open_access_journal_home(self):
        """
        Testa se os links e o conteúdo da licença esta de acordo com a licença
        cadastrada na coleção.
        """

        with current_app.app_context():
            collection = utils.makeOneCollection()

            journal = utils.makeOneJournal()

            with self.client as c:

                response = c.get(url_for('main.journal_detail',
                                         journal_id=journal.id))

                self.assertStatus(response, 200)

                self.assertTemplateUsed('journal/detail.html')

                self.assertIn('/static/img/oa_logo_32.png', response.data)
                self.assertIn('href="%s"' % url_for('main.open_access'), response.data)
                self.assertIn('Open Access', response.data)

    def test_journal_open_access_journal_home(self):
        """
        Testa se os links e o conteúdo da licença este de acordo com a licença
        cadastrado no periódico.
        """

        with current_app.app_context():
            collection = utils.makeOneCollection()

            journal = utils.makeOneJournal()

            with self.client as c:

                response = c.get(url_for('main.journal_detail',
                                         journal_id=journal.id))

                self.assertStatus(response, 200)

                self.assertTemplateUsed('journal/detail.html')

                self.assertIn('/static/img/oa_logo_32.png', response.data)
                self.assertIn('href="%s"' % url_for('main.open_access'), response.data)
                self.assertIn('Open Access', response.data)

    def test_journal_open_access_in_issue_grid(self):
        """
        Testa se os links e o conteúdo da licença este de acordo com a licença
        cadastrado no periódico.
        """

        with current_app.app_context():
            collection = utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({'journal': journal})

            with self.client as c:

                response = c.get(url_for('main.issue_grid',
                                         journal_id=journal.id))

                self.assertStatus(response, 200)

                self.assertTemplateUsed('issue/grid.html')

                self.assertIn('/static/img/oa_logo_32.png', response.data)
                self.assertIn('href="%s"' % url_for('main.open_access'), response.data)
                self.assertIn('Open Access', response.data)

    def test_journal_open_access_in_issue_toc(self):
        """
        Testa se os links e o conteúdo da licença este de acordo com a licença
        cadastrado no periódico.
        """

        with current_app.app_context():
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue()

            with self.client as c:

                response = c.get(url_for('main.issue_toc',
                                         issue_id=issue.id))

                self.assertStatus(response, 200)

                self.assertTemplateUsed('issue/toc.html')

                self.assertIn('/static/img/oa_logo_32.png', response.data)
                self.assertIn('href="%s"' % url_for('main.open_access'), response.data)
                self.assertIn('Open Access', response.data)

    def test_journal_open_access(self):
        """
        Testa se os links e o conteúdo da licença este de acordo com a licença
        cadastrado no periódico.
        """

        with current_app.app_context():
            collection = utils.makeOneCollection()

            journal = utils.makeOneJournal()

            with self.client as c:

                response = c.get(url_for('main.journal_detail',
                                         journal_id=journal.id))

                self.assertStatus(response, 200)

                self.assertTemplateUsed('journal/detail.html')

                # Collection license
                self.assertIn('/static/img/oa_logo_32.png', response.data)
                self.assertIn('href="%s"' % url_for('main.open_access'), response.data)
                self.assertIn('Open Access', response.data)

