# coding: utf-8

from unittest.mock import patch, Mock

from flask import current_app, url_for
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

    def test_journal_home_check_redirect(self):
        """
        Testa o acesso a home da revista pela URL antiga.
        URL testa: scielo.php?script=sci_serial&pid=ISSN
        """

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000'})

            with self.client as c:

                url = 'scielo.php?script=sci_serial&pid=%s' % journal.print_issn

                response = c.get(url)

                self.assertStatus(response, 301)

    def test_issue_grid(self):
        """
        Testa o acesso a grade de números da revista pela URL antiga.
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

    def test_issue_grid_check_redirect(self):
        """
        Testa o acesso a grade de números da revista pela URL antiga.
        URL testa: scielo.php?script=sci_issues&pid=ISSN
        """

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000'})

            issue = utils.makeOneIssue({'journal': journal.id, 'pid': '0000-0000'})

            with self.client as c:

                url = 'scielo.php?script=sci_issues&pid=%s' % issue.pid

                response = c.get(url)

                self.assertStatus(response, 301)

    def test_issue_toc(self):
        """
        Testa o acesso ao toc de um números pela URL antiga.
        URL testa: scielo.php?script=sci_issuetoc&pid=ISSN + ID DO número
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

    def test_issue_toc_check_redirect(self):
        """
        Testa o acesso ao toc de um números pela URL antiga.
        URL testa: scielo.php?script=sci_issuetoc&pid=ISSN + ID DO número
        """

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000'})

            issue = utils.makeOneIssue({
                'journal': journal.id,
                'pid': '0000-000020160001'
            })

            with self.client as c:

                url = 'scielo.php?script=sci_issuetoc&pid=%s' % issue.pid

                response = c.get(url)

                self.assertStatus(response, 301)

    def test_article_text(self):
        """
        Testa o acesso ao artigo pela URL antiga.
        URL testa: scielo.php?script=sci_serial&pid=ISSN + ID DO número + ID DO ARTIGO
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

    def test_article_text_check_redirect(self):
        """
        Testa o acesso ao artigo pela URL antiga.
        URL testa: scielo.php?script=sci_serial&pid=ISSN + ID DO número + ID DO ARTIGO
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

                response = c.get(url)

                self.assertStatus(response, 301)

    @patch('requests.get')
    def test_router_legacy_pdf(self, mocked_requests_get):
        """
        Testa o acesso à URL antiga do PDF quando existe a chave filename no campo pdf.
        URL testada: /pdf/<JOURNAL_ACRON>/<ISSUE_LABEL>/<PDF_FILENAME>
            Exemplo: /pdf/cta/v39s2/0101-2061-cta-fst22918.pdf
        """

        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b'<pdf>'
        mocked_requests_get.return_value = mocked_response

        with current_app.app_context():

            journal = utils.makeOneJournal({'print_issn': '0000-0000', 'acronym': 'cta'},)

            issue = utils.makeOneIssue({
                'journal': journal.id,
                'label': 'v39s2',
            })

            article = utils.makeOneArticle({
                'journal': journal.id,
                'issue': issue.id,
                'pdfs': [
                    {
                        'lang': 'en',
                        'url': 'http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf',
                        'file_path': '/pdf/cta/v39s2/0101-2061-cta-fst30618.pdf',
                        'type': 'pdf'
                    }
                ]
            })

            with self.client as c:

                url = '/pdf/cta/v39s2/0101-2061-cta-fst30618.pdf'

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

    def test_article_text_with_lng(self):
        """
        Testa o acesso ao artigo pela URL antiga.
        URL testa: scielo.php?script=sci_arttext&pid=ISSN + ID DO número + ID  + idioma DO ARTIGO
        Exemplo: scielo.php?script=sci_arttext&pid=0000-000020160001&tlng=en
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
                'pid': '0000-00002016000100251',

            })

            with self.client as c:

                url = 'scielo.php?script=sci_arttext&pid=%s&tlng=%s' % (article.pid, 'en')

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed('article/detail.html')

    def test_article_text_return_redirect_from_legacy_urls(self):
        """
        Testa o acesso ao artigo pela URL antiga.
        URL testa: scielo.php?script=sci_arttext&pid=ISSN + ID DO número + ID  + idioma DO ARTIGO
        Exemplo: scielo.php?script=sci_arttext&pid=0000-000020160001&tlng=en
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
                'pid': '0000-00002016000100251',

            })

            with self.client as c:

                url = 'scielo.php?script=sci_arttext&pid=%s&tlng=%s' % (article.pid, 'en')

                response = c.get(url)

                self.assertStatus(response, 301)

    def test_article_abstract(self):
        """
        Testa o acesso ao abstract do artigo pela URL antiga.
        URL testa: scielo.php?script=sci_abstract&pid=ISSN + ID DO número + ID DO ARTIGO
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

    def test_scielo_php_redirect_to_home(self):
        """
        acessar a url: /scielo.php (sem querystring) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # collection = utils.makeOneCollection()
            # when
            response_no_follow = self.client.get(url_for('main.router_legacy'), follow_redirects=False)
            response_following = self.client.get(url_for('main.router_legacy'), follow_redirects=True)
            # then
            self.assertStatus(response_no_follow, 302)
            self.assertStatus(response_following, 200)
            self.assertEqual('text/html; charset=utf-8', response_following.content_type)
            self.assert_template_used("collection/index.html")

    def test_scielo_php_with_unexpected_qs_redirect_to_home(self):
        """
        acessar a url: /scielo.php?foo=bar vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # collection = utils.makeOneCollection()
            # when
            qs = '?foo=bar'
            response = self.client.get(url_for('main.router_legacy') + qs, follow_redirects=True)

            # then
            self.assertStatus(response, 200)
            self.assertEqual('text/html; charset=utf-8', response.content_type)
            self.assert_template_used("collection/index.html")

    def test_scielo_php_with_invalid_script_must_redirect_to_home(self):
        """
        acessar a url: /scielo.php?script=foo (foo é valor incorreto, sem pid) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = '?script=foo'
            response = self.client.get(url_for('main.router_legacy') + qs, follow_redirects=True)

            # then
            self.assertStatus(response, 200)
            self.assertEqual('text/html; charset=utf-8', response.content_type)
            self.assert_template_used("collection/index.html")

    def test_scielo_php_with_sci_serial_script_but_incorrect_pid_must_redirect_to_home(self):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = '?script=sci_serial&pid='
            response = self.client.get(url_for('main.router_legacy') + qs, follow_redirects=True)

            # then
            self.assertStatus(response, 400)
            self.assertEqual('text/html; charset=utf-8', response.content_type)
            self.assert_template_used("errors/400.html")

    def test_scielo_php_with_sci_issuetoc_script_but_incorrect_pid_must_redirect_to_home(self):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = '?script=sci_issuetoc&pid='
            response = self.client.get(url_for('main.router_legacy') + qs, follow_redirects=True)

            # then
            self.assertStatus(response, 400)
            self.assertEqual('text/html; charset=utf-8', response.content_type)
            self.assert_template_used("errors/400.html")

    def test_scielo_php_with_sci_arttext_script_but_incorrect_pid_must_redirect_to_home(self):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = '?script=sci_arttext&pid='
            response = self.client.get(url_for('main.router_legacy') + qs, follow_redirects=True)

            # then
            self.assertStatus(response, 400)
            self.assertEqual('text/html; charset=utf-8', response.content_type)
            self.assert_template_used("errors/400.html")

    def test_scielo_php_with_sci_abstract_script_but_incorrect_pid_must_redirect_to_home(self):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = '?script=sci_arttext&pid='
            response = self.client.get(url_for('main.router_legacy') + qs, follow_redirects=True)

            # then
            self.assertStatus(response, 400)
            self.assertEqual('text/html; charset=utf-8', response.content_type)
            self.assert_template_used("errors/400.html")

    def test_scielo_php_with_sci_issues_script_but_incorrect_pid_must_redirect_to_home(self):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = '?script=sci_issues&pid='
            response = self.client.get(url_for('main.router_legacy') + qs, follow_redirects=True)

            # then
            self.assertStatus(response, 400)
            self.assertEqual('text/html; charset=utf-8', response.content_type)
            self.assert_template_used("errors/400.html")

    def test_scielo_php_with_sci_pdf_script_but_incorrect_pid_must_redirect_to_home(self):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = '?script=sci_pdf&pid='
            response = self.client.get(url_for('main.router_legacy') + qs, follow_redirects=True)

            # then
            self.assertStatus(response, 400)
            self.assertEqual('text/html; charset=utf-8', response.content_type)
            self.assert_template_used("errors/400.html")
