# coding: utf-8

from flask import current_app, url_for

from . import utils
from .base import BaseTestCase


class FooterTestCase(BaseTestCase):
    def test_collection_open_access_home(self):
        """
        Testa se os links e o conteúdo da licença esta de acordo com a licença
        cadastrada na coleção.
        """

        with current_app.app_context():
            utils.makeOneCollection()

            with self.client as c:
                response = c.get(url_for("main.index"))

                self.assertStatus(response, 200)

                self.assertTemplateUsed("collection/index.html")

                self.assertIn(b"/static/img/oa_logo_32.png", response.data)
                self.assertIn(
                    'href="%s"' % url_for("main.about_collection"),
                    response.data.decode("utf-8"),
                )
                self.assertIn(b"Open Access", response.data)

    def test_collection_open_access_list_theme(self):
        """
        Testa se os links e o conteúdo da licença esta de acordo com a licença
        cadastrada na coleção.
        """
        with current_app.app_context():
            utils.makeOneCollection()

            with self.client as c:
                response = c.get(url_for("main.collection_list"))
                self.assertStatus(response, 200)

                self.assertTemplateUsed("collection/list_journal.html")

                self.assertIn(b"/static/img/oa_logo_32.png", response.data)
                self.assertIn(
                    'href="%s"' % url_for("main.about_collection"),
                    response.data.decode("utf-8"),
                )
                self.assertIn(b"Open Access", response.data)

    def test_collection_open_access_journal_home(self):
        """
        Testa se os links e o conteúdo da licença esta de acordo com a licença
        cadastrada na coleção.
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            with self.client as c:
                response = c.get(
                    url_for("main.journal_detail", url_seg=journal.url_segment)
                )

                self.assertStatus(response, 200)

                self.assertTemplateUsed("journal/detail.html")

                self.assertIn(b"/static/img/oa_logo_32.png", response.data)
                self.assertIn(
                    'href="%s"' % url_for("main.about_collection"),
                    response.data.decode("utf-8"),
                )
                self.assertIn(b"Open Access", response.data)

    def test_journal_open_access_journal_home(self):
        """
        Testa se os links e o conteúdo da licença este de acordo com a licença
        cadastrado no periódico.
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            with self.client as c:
                response = c.get(
                    url_for("main.journal_detail", url_seg=journal.url_segment)
                )

                self.assertStatus(response, 200)

                self.assertTemplateUsed("journal/detail.html")

                self.assertIn(b"/static/img/oa_logo_32.png", response.data)
                self.assertIn(
                    'href="%s"' % url_for("main.about_collection"),
                    response.data.decode("utf-8"),
                )
                self.assertIn(b"Open Access", response.data)

    def test_journal_open_access_in_issue_grid(self):
        """
        Testa se os links e o conteúdo da licença este de acordo com a licença
        cadastrado no periódico.
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            utils.makeOneIssue({"journal": journal})

            with self.client as c:
                response = c.get(
                    url_for("main.issue_grid", url_seg=journal.url_segment)
                )

                self.assertStatus(response, 200)

                self.assertTemplateUsed("issue/grid.html")

                self.assertIn(b"/static/img/oa_logo_32.png", response.data)
                self.assertIn(
                    'href="%s"' % url_for("main.about_collection"),
                    response.data.decode("utf-8"),
                )
                self.assertIn(b"Open Access", response.data)

    def test_journal_open_access_in_issue_toc(self):
        """
        Testa se os links e o conteúdo da licença este de acordo com a licença
        cadastrado no periódico.
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({"journal": journal})

            with self.client as c:
                response = c.get(
                    url_for(
                        "main.issue_toc",
                        url_seg=issue.journal.url_segment,
                        url_seg_issue=issue.url_segment,
                    )
                )

                self.assertStatus(response, 200)

                self.assertTemplateUsed("issue/toc.html")

                self.assertIn(b"/static/img/oa_logo_32.png", response.data)
                self.assertIn(
                    'href="%s"' % url_for("main.about_collection"),
                    response.data.decode("utf-8"),
                )
                self.assertIn(b"Open Access", response.data)

    def test_journal_open_access(self):
        """
        Testa se os links e o conteúdo da licença este de acordo com a licença
        cadastrado no periódico.
        """

        with current_app.app_context():
            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            with self.client as c:
                response = c.get(
                    url_for("main.journal_detail", url_seg=journal.url_segment)
                )

                self.assertStatus(response, 200)

                self.assertTemplateUsed("journal/detail.html")

                # Collection license
                self.assertIn(b"/static/img/oa_logo_32.png", response.data)
                self.assertIn(
                    'href="%s"' % url_for("main.about_collection"),
                    response.data.decode("utf-8"),
                )
                self.assertIn(b"Open Access", response.data)
