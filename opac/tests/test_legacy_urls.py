# coding: utf-8

from flask import current_app
from .base import BaseTestCase

from . import utils


class LegacyURLTestCase(BaseTestCase):

    def test_journal_home(self):
        """
        Testa o acesso a home da revista pela URL antiga.
        URL testa: scielo.php?script=sci_serial&pid=ISSN
        """

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000'})

            with self.client as c:

                url = 'scielo.php?script=sci_serial&pid=%s' % journal.print_issn

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed('journal/detail.html')

    def test_issue_grid(self):
        """
        Testa o acesso a grade de fascículos da revista pela URL antiga.
        URL testa: scielo.php?script=sci_issues&pid=ISSN
        """

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000'})

            issue = utils.makeOneIssue({'journal': journal.id, 'pid': '0000-0000'})

            with self.client as c:

                url = 'scielo.php?script=sci_issues&pid=%s' % issue.pid

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed('issue/grid.html')

    def test_issue_toc(self):
        """
        Testa o acesso ao toc de um fascículos pela URL antiga.
        URL testa: scielo.php?script=sci_issuetoc&pid=ISSN + ID DO FASCÍCULO
        """

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000'})

            issue = utils.makeOneIssue({
                'journal': journal.id,
                'pid': '0000-000020160001'
            })

            with self.client as c:

                url = 'scielo.php?script=sci_issuetoc&pid=%s' % issue.pid

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed('issue/toc.html')

    def test_article_text(self):
        """
        Testa o acesso ao artigo pela URL antiga.
        URL testa: scielo.php?script=sci_serial&pid=ISSN + ID DO FASCÍCULO + ID DO ARTIGO
        """

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000'})

            issue = utils.makeOneIssue({
                'journal': journal.id,
                'pid': '0000-000020160001'
            })

            article = utils.makeOneArticle({
                'journal': journal.id,
                'issue': issue.id,
                'pid': '0000-00002016000100251'
            })

            with self.client as c:

                url = 'scielo.php?script=sci_arttext&pid=%s' % article.pid

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed('article/detail.html')

    def test_article_abstract(self):
        """
        Testa o acesso ao abstract do artigo pela URL antiga.
        URL testa: scielo.php?script=sci_abstract&pid=ISSN + ID DO FASCÍCULO + ID DO ARTIGO
        """

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000'})

            issue = utils.makeOneIssue({
                'journal': journal.id,
                'pid': '0000-000020160001'
            })

            article = utils.makeOneArticle({
                'journal': journal.id, 'issue': issue.id,
                'pid': '0000-00002016000100251'
            })

            with self.client as c:

                url = 'scielo.php?script=sci_abstract&pid=%s' % article.pid

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed('article/detail.html')
