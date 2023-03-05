# coding: utf-8

from unittest.mock import Mock, patch
from urllib.parse import urlparse

from flask import current_app, url_for

from . import utils
from .base import BaseTestCase


class LegacyURLTestCase(BaseTestCase):
    def test_journal_home(self):
        """
        Testa o acesso a home da revista pela URL antiga.
        URL testa: scielo.php?script=sci_serial&pid=ISSN
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            with self.client as c:
                url = "scielo.php?script=sci_serial&pid=%s" % journal.print_issn

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed("journal/detail.html")

    def test_journal_home_check_redirect(self):
        """
        Testa o acesso a home da revista pela URL antiga.
        URL testa: scielo.php?script=sci_serial&pid=ISSN
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            with self.client as c:
                url = "scielo.php?script=sci_serial&pid=%s" % journal.print_issn

                response = c.get(url)

                self.assertStatus(response, 301)

    def test_issue_grid(self):
        """
        Testa o acesso a grade de números da revista pela URL antiga.
        URL testa: scielo.php?script=sci_issues&pid=ISSN
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue({"journal": journal.id, "pid": "0000-0000"})

            with self.client as c:
                url = "scielo.php?script=sci_issues&pid=%s" % issue.pid

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed("issue/grid.html")

    def test_issue_grid_check_redirect(self):
        """
        Testa o acesso a grade de números da revista pela URL antiga.
        URL testa: scielo.php?script=sci_issues&pid=ISSN
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue({"journal": journal.id, "pid": "0000-0000"})

            with self.client as c:
                url = "scielo.php?script=sci_issues&pid=%s" % issue.pid

                response = c.get(url)

                self.assertStatus(response, 301)

    def test_issue_toc(self):
        """
        Testa o acesso ao toc de um números pela URL antiga.
        URL testa: scielo.php?script=sci_issuetoc&pid=ISSN + ID DO número
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000020160001"}
            )

            with self.client as c:
                url = "scielo.php?script=sci_issuetoc&pid=%s" % issue.pid

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed("issue/toc.html")

    def test_issue_toc_check_redirect(self):
        """
        Testa o acesso ao toc de um números pela URL antiga.
        URL testa: scielo.php?script=sci_issuetoc&pid=ISSN + ID DO número
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000020160001"}
            )

            with self.client as c:
                url = "scielo.php?script=sci_issuetoc&pid=%s" % issue.pid

                response = c.get(url)

                self.assertStatus(response, 301)

    def test_article_text(self):
        """
        Testa o acesso ao artigo pela URL antiga.
        URL testa: scielo.php?script=sci_serial&pid=ISSN + ID DO número + ID DO ARTIGO
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000020160001"}
            )

            article = utils.makeOneArticle(
                {
                    "journal": journal.id,
                    "issue": issue.id,
                    "pid": "0000-00002016000100251",
                }
            )

            with self.client as c:
                url = "scielo.php?script=sci_arttext&pid=%s" % article.pid

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed("article/detail.html")

    def test_article_text_looking_scielo_pids(self):
        """
        Testa o acesso ao artigo pela URL antiga considerando o campo ``scielo_pids``.
        URL testa: scielo.php?script=sci_serial&pid=ISSN + ID DO número + ID DO ARTIGO
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000000000000"}
            )

            article = utils.makeOneArticle(
                {
                    "journal": journal.id,
                    "issue": issue.id,
                    "pid": "0000-00000000000000001",
                    "scielo_pids": {
                        "v2": "0000-00000000000000002",
                        "v3": "0000-00000000000000003",
                        "other": ["0000-00000000000000002"],
                    },
                }
            )

            with self.client as c:
                for pid in ["0000-00000000000000001", "0000-00000000000000002"]:
                    with self.subTest(pid):
                        url = "scielo.php?script=sci_arttext&pid=%s" % pid
                        response = c.get(url, follow_redirects=True)
                        self.assertStatus(response, 200)
                        self.assertTemplateUsed("article/detail.html")

    def test_article_text_check_redirect(self):
        """
        Testa o acesso ao artigo pela URL antiga.
        URL testa: scielo.php?script=sci_serial&pid=ISSN + ID DO número + ID DO ARTIGO
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000020160001"}
            )

            article = utils.makeOneArticle(
                {
                    "journal": journal.id,
                    "issue": issue.id,
                    "pid": "0000-00002016000100251",
                }
            )

            with self.client as c:
                url = "scielo.php?script=sci_arttext&pid=%s" % article.pid

                response = c.get(url)

                self.assertStatus(response, 301)

    @patch("requests.get")
    def test_article_pdf(self, mocked_requests_get):
        """
        Testa o acesso ao PDF pela URL antiga verificando em todas as versões do pid
        campo ``scielo_pids``.
        URL testa: scielo.php?script=sci_pdf&pid=ISSN + ID DO número + ID DO ARTIGO
        """
        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b"<pdf>"
        mocked_requests_get.return_value = mocked_response

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000000000000"}
            )

            article = utils.makeOneArticle(
                {
                    "journal": journal.id,
                    "issue": issue.id,
                    "original_language": "en",
                    "pid": "0000-00000000000000001",
                    "pdfs": [
                        {
                            "lang": "en",
                            "url": "http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618.pdf",
                            "type": "pdf",
                        }
                    ],
                }
            )

            with self.client as c:
                url = "scielo.php?script=sci_pdf&pid=%s" % article.pid

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

    @patch("requests.get")
    def test_article_pdf_with_tlng(self, mocked_requests_get):
        """
        Testa o acesso ao PDF pela URL antiga verificando em todas as versões do pid
        campo ``scielo_pids`` e considerando o idioma do PDF e garante que o redirect para o a URL PID v3 está correta.
        URL testa: scielo.php?script=sci_pdf&pid=ISSN + ID DO número + ID DO ARTIGO&tlng=LANG CODE ["pt", "es", "en"]
        """

        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b"<es_content>"
        mocked_requests_get.return_value = mocked_response

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000000000000"}
            )

            article = utils.makeOneArticle(
                {
                    "_id": "2586f2aadb65457c94fcee24c48b3d6c",
                    "journal": journal.id,
                    "issue": issue.id,
                    "original_language": "en",
                    "pid": "0000-00000000000000001",
                    "pdfs": [
                        {
                            "lang": "en",
                            "url": "http://minio:9000/documentstore/1678-457X/2586f2aadb65457c94fcee24c48b3d6c/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618-en.pdf",
                            "type": "pdf",
                        },
                        {
                            "lang": "pt",
                            "url": "http://minio:9000/documentstore/1678-457X/2586f2aadb65457c94fcee24c48b3d6c/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618.pdf",
                            "type": "pdf",
                        },
                        {
                            "lang": "es",
                            "url": "http://minio:9000/documentstore/1678-457X/2586f2aadb65457c94fcee24c48b3d6c/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618-es.pdf",
                            "type": "pdf",
                        },
                    ],
                }
            )

            # Verifica o conteúdo do PDF com es(espanhol)
            with self.client as c:
                url = "scielo.php?script=sci_pdf&pid=%s&tlng=es" % article.pid

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)
                self.assertEqual(response.data, b"<es_content>")

            # Verifica se o redirect para a URL com PID v3 está correta
            with self.client as c:
                url = "scielo.php?script=sci_pdf&pid=%s&tlng=es" % article.pid

                response = c.get(url, follow_redirects=False)

                expectedPath = "/j/journal_acron/a/2586f2aadb65457c94fcee24c48b3d6c/"
                expectedQuery = "format=pdf&lang=es"

                self.assertStatus(response, 301)
                self.assertEqual(urlparse(response.location).path, expectedPath)
                self.assertEqual(urlparse(response.location).query, expectedQuery)

    @patch("requests.get")
    def test_article_pdf_without_tlng(self, mocked_requests_get):
        """
        Testa o acesso ao PDF pela URL antiga sem o tlng, considera o idioma original
        quando não existe o tlng.
        URL testa: scielo.php?script=sci_pdf&pid=ISSN + ID DO número + ID DO ARTIGO
        """

        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b"<en_content>"
        mocked_requests_get.return_value = mocked_response

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000000000000"}
            )

            article = utils.makeOneArticle(
                {
                    "_id": "2586f2aadb65457c94fcee24c48b3d6c",
                    "journal": journal.id,
                    "issue": issue.id,
                    "original_language": "en",
                    "pid": "0000-00000000000000001",
                    "pdfs": [
                        {
                            "lang": "en",
                            "url": "http://minio:9000/documentstore/1678-457X/2586f2aadb65457c94fcee24c48b3d6c/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618-en.pdf",
                            "type": "pdf",
                        },
                        {
                            "lang": "pt",
                            "url": "http://minio:9000/documentstore/1678-457X/2586f2aadb65457c94fcee24c48b3d6c/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618.pdf",
                            "type": "pdf",
                        },
                        {
                            "lang": "es",
                            "url": "http://minio:9000/documentstore/1678-457X/2586f2aadb65457c94fcee24c48b3d6c/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618-es.pdf",
                            "type": "pdf",
                        },
                    ],
                }
            )

            # Verifica o conteúdo do PDF com en(espanhol)
            with self.client as c:
                url = "scielo.php?script=sci_pdf&pid=%s" % article.pid

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)
                self.assertEqual(response.data, b"<en_content>")

            # Verifica se o redirect para a URL com PID v3 está correta
            with self.client as c:
                url = "scielo.php?script=sci_pdf&pid=%s&" % article.pid

                response = c.get(url, follow_redirects=False)

                expectedPath = "/j/journal_acron/a/2586f2aadb65457c94fcee24c48b3d6c/"
                expectedQuery = "format=pdf"

                self.assertStatus(response, 301)
                self.assertEqual(urlparse(response.location).path, expectedPath)
                self.assertEqual(urlparse(response.location).query, expectedQuery)

    @patch("requests.get")
    def test_article_pdf_when_dont_have_the_pdf_translation(self, mocked_requests_get):
        """
        Testa o acesso ao PDF pela URL antiga verificando em todas as versões do pid
        campo ``scielo_pids`` e retornando o primeiro encontrado quando não existe a traduçã
        URL testa: scielo.php?script=sci_pdf&pid=ISSN + ID DO número + ID DO ARTIGO&tlng=LANG CODE ["pt", "es", "en"]
        """

        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b"<content>"
        mocked_requests_get.return_value = mocked_response

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000000000000"}
            )

            article = utils.makeOneArticle(
                {
                    "_id": "2586f2aadb65457c94fcee24c48b3d6c",
                    "journal": journal.id,
                    "issue": issue.id,
                    "original_language": "en",
                    "pid": "0000-00000000000000001",
                    "pdfs": [
                        {
                            "lang": "en",
                            "url": "http://minio:9000/documentstore/1678-457X/2586f2aadb65457c94fcee24c48b3d6c/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618-en.pdf",
                            "type": "pdf",
                        },
                        {
                            "lang": "pt",
                            "url": "http://minio:9000/documentstore/1678-457X/2586f2aadb65457c94fcee24c48b3d6c/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618.pdf",
                            "type": "pdf",
                        },
                        {
                            "lang": "es",
                            "url": "http://minio:9000/documentstore/1678-457X/2586f2aadb65457c94fcee24c48b3d6c/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618-es.pdf",
                            "type": "pdf",
                        },
                    ],
                }
            )

            # Verifica se o redirect para a URL com PID v3 está correta
            with self.client as c:
                url = "scielo.php?script=sci_pdf&pid=%s&tlng=xxx" % article.pid

                response = c.get(url, follow_redirects=False)

                expectedPath = "/j/journal_acron/a/2586f2aadb65457c94fcee24c48b3d6c/"
                expectedQuery = "format=pdf&lang=xxx"

                self.assertStatus(response, 301)
                self.assertEqual(urlparse(response.location).path, expectedPath)
                self.assertEqual(urlparse(response.location).query, expectedQuery)

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)
                self.assertEqual(response.data, b"<content>")

    @patch("requests.get")
    def test_article_pdf_looking_scielo_pids(self, mocked_requests_get):
        """
        Testa o acesso ao PDF pela URL antiga verificando em todas as versões do pid
        campo ``scielo_pids``.
        URL testa: scielo.php?script=sci_pdf&pid=ISSN + ID DO número + ID DO ARTIGO
        """
        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b"<pdf>"
        mocked_requests_get.return_value = mocked_response

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000000000000"}
            )

            article = utils.makeOneArticle(
                {
                    "journal": journal.id,
                    "issue": issue.id,
                    "original_language": "en",
                    "pid": "0000-00000000000000001",
                    "scielo_pids": {
                        "v2": "0000-00000000000000002",
                        "v3": "0000-00000000000000003",
                        "other": ["0000-00000000000000002"],
                    },
                    "pdfs": [
                        {
                            "lang": "en",
                            "url": "http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "file_path": "/pdf/cta/v39s2/0101-2061-cta-fst30618.pdf",
                            "type": "pdf",
                        }
                    ],
                }
            )

            with self.client as c:
                for pid in ["0000-00000000000000001", "0000-00000000000000002"]:
                    with self.subTest(pid):
                        url = "scielo.php?script=sci_pdf&pid=%s" % pid
                        response = c.get(url, follow_redirects=False)
                        self.assertStatus(response, 301)

    @patch("requests.get")
    def test_router_legacy_pdf(self, mocked_requests_get):
        """
        Testa o acesso à URL antiga do PDF quando existe a chave filename no campo pdf.
        URL testada: /pdf/<JOURNAL_ACRON>/<ISSUE_LABEL>/<PDF_FILENAME>
            Exemplo: /pdf/cta/v39s2/0101-2061-cta-fst22918.pdf
        """

        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b"<pdf>"
        mocked_requests_get.return_value = mocked_response

        with current_app.app_context():
            journal = utils.makeOneJournal(
                {"print_issn": "0000-0000", "acronym": "cta"},
            )

            issue = utils.makeOneIssue(
                {
                    "journal": journal.id,
                    "label": "v39s2",
                }
            )

            article = utils.makeOneArticle(
                {
                    "journal": journal.id,
                    "issue": issue.id,
                    "pdfs": [
                        {
                            "lang": "en",
                            "url": "http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "filename": "0101-2061-cta-fst30618.pdf",
                            "type": "pdf",
                        }
                    ],
                }
            )

            with self.client as c:
                url = "/pdf/cta/v39s2/0101-2061-cta-fst30618.pdf"

                response = c.get(url, follow_redirects=False)

                self.assertStatus(response, 301)

    @patch("requests.get")
    def test_router_legacy_pdf_suppl_material(self, mocked_requests_get):
        """
        Testa o acesso à URL antiga do PDF de material suplementar quando existe
        a chave filename no campo pdf.
        URL testada: /pdf/<JOURNAL_ACRON>/<ISSUE_LABEL>/<PDF_FILENAME>
            Exemplo: /pdf/cta/v39s2/0101-2061-cta-suppl01.pdf
        """

        mocked_response = Mock()
        mocked_response.status_code = 200
        mocked_response.content = b"<pdf>"
        mocked_requests_get.return_value = mocked_response

        with current_app.app_context():
            journal = utils.makeOneJournal(
                {"print_issn": "0000-0000", "acronym": "cta"},
            )

            issue = utils.makeOneIssue(
                {
                    "journal": journal.id,
                    "label": "v92n2",
                }
            )

            article = utils.makeOneArticle(
                {
                    "journal": journal.id,
                    "issue": issue.id,
                    "mat_suppl": [
                        {
                            "url": "http://minio:9000/documentstore/1678-457X/JDH74Jr4SyDVpnkMyrqkDhF/e5e09c7d5e4e5052868372df837de4e1ee9d651a.pdf",
                            "filename": "0101-2061-cta-suppl01.pdf",
                        }
                    ],
                }
            )

            with self.client as c:
                url = "/pdf/cta/v92n2/0101-2061-cta-suppl01.pdf"

                response = c.get(url, follow_redirects=False)

                self.assertStatus(response, 301)

    def test_article_text_with_lng(self):
        """
        Testa o acesso ao artigo pela URL antiga.
        URL testa: scielo.php?script=sci_arttext&pid=ISSN + ID DO número + ID  + idioma DO ARTIGO
        Exemplo: scielo.php?script=sci_arttext&pid=0000-000020160001&tlng=en
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000020160001"}
            )

            article = utils.makeOneArticle(
                {
                    "journal": journal.id,
                    "issue": issue.id,
                    "pid": "0000-00002016000100251",
                }
            )

            with self.client as c:
                url = "scielo.php?script=sci_arttext&pid=%s&tlng=%s" % (
                    article.pid,
                    "en",
                )

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed("article/detail.html")

    def test_article_text_return_redirect_from_legacy_urls(self):
        """
        Testa o acesso ao artigo pela URL antiga.
        URL testa: scielo.php?script=sci_arttext&pid=ISSN + ID DO número + ID  + idioma DO ARTIGO
        Exemplo: scielo.php?script=sci_arttext&pid=0000-000020160001&tlng=en
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000020160001"}
            )

            article = utils.makeOneArticle(
                {
                    "journal": journal.id,
                    "issue": issue.id,
                    "pid": "0000-00002016000100251",
                }
            )

            with self.client as c:
                url = "scielo.php?script=sci_arttext&pid=%s&tlng=%s" % (
                    article.pid,
                    "en",
                )

                response = c.get(url)

                self.assertStatus(response, 301)

    def test_article_abstract(self):
        """
        Testa o acesso ao abstract do artigo pela URL antiga.
        URL testa: scielo.php?script=sci_abstract&pid=ISSN + ID DO número + ID DO ARTIGO
        """

        with current_app.app_context():
            journal = utils.makeOneJournal({"print_issn": "0000-0000"})

            issue = utils.makeOneIssue(
                {"journal": journal.id, "pid": "0000-000020160001"}
            )

            article = utils.makeOneArticle(
                {
                    "journal": journal.id,
                    "issue": issue.id,
                    "pid": "0000-00002016000100251",
                    "abstracts": [
                        {"language": "pt", "text": "Texto do abstract"},
                    ],
                }
            )

            with self.client as c:
                url = "scielo.php?script=sci_abstract&pid=%s" % article.pid

                response = c.get(url, follow_redirects=True)

                self.assertStatus(response, 200)

                self.assertTemplateUsed("article/detail.html")

    def test_scielo_php_redirect_to_home(self):
        """
        acessar a url: /scielo.php (sem querystring) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # collection = utils.makeOneCollection()
            # when
            response_no_follow = self.client.get(
                url_for("main.router_legacy"), follow_redirects=False
            )
            response_following = self.client.get(
                url_for("main.router_legacy"), follow_redirects=True
            )
            # then
            self.assertStatus(response_no_follow, 302)
            self.assertStatus(response_following, 200)
            self.assertEqual(
                "text/html; charset=utf-8", response_following.content_type
            )
            self.assert_template_used("collection/index.html")

    def test_scielo_php_with_unexpected_qs_redirect_to_home(self):
        """
        acessar a url: /scielo.php?foo=bar vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # collection = utils.makeOneCollection()
            # when
            qs = "?foo=bar"
            response = self.client.get(
                url_for("main.router_legacy") + qs, follow_redirects=True
            )

            # then
            self.assertStatus(response, 200)
            self.assertEqual("text/html; charset=utf-8", response.content_type)
            self.assert_template_used("collection/index.html")

    def test_scielo_php_with_invalid_script_must_redirect_to_home(self):
        """
        acessar a url: /scielo.php?script=foo (foo é valor incorreto, sem pid) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = "?script=foo"
            response = self.client.get(
                url_for("main.router_legacy") + qs, follow_redirects=True
            )

            # then
            self.assertStatus(response, 200)
            self.assertEqual("text/html; charset=utf-8", response.content_type)
            self.assert_template_used("collection/index.html")

    def test_scielo_php_with_sci_serial_script_but_incorrect_pid_must_redirect_to_home(
        self,
    ):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = "?script=sci_serial&pid="
            response = self.client.get(
                url_for("main.router_legacy") + qs, follow_redirects=True
            )

            # then
            self.assertStatus(response, 400)
            self.assertEqual("text/html; charset=utf-8", response.content_type)
            self.assert_template_used("errors/400.html")

    def test_scielo_php_with_sci_issuetoc_script_but_incorrect_pid_must_redirect_to_home(
        self,
    ):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = "?script=sci_issuetoc&pid="
            response = self.client.get(
                url_for("main.router_legacy") + qs, follow_redirects=True
            )

            # then
            self.assertStatus(response, 400)
            self.assertEqual("text/html; charset=utf-8", response.content_type)
            self.assert_template_used("errors/400.html")

    def test_scielo_php_with_sci_arttext_script_but_incorrect_pid_must_redirect_to_home(
        self,
    ):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = "?script=sci_arttext&pid="
            response = self.client.get(
                url_for("main.router_legacy") + qs, follow_redirects=True
            )

            # then
            self.assertStatus(response, 400)
            self.assertEqual("text/html; charset=utf-8", response.content_type)
            self.assert_template_used("errors/400.html")

    def test_scielo_php_with_sci_abstract_script_but_incorrect_pid_must_redirect_to_home(
        self,
    ):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = "?script=sci_arttext&pid="
            response = self.client.get(
                url_for("main.router_legacy") + qs, follow_redirects=True
            )

            # then
            self.assertStatus(response, 400)
            self.assertEqual("text/html; charset=utf-8", response.content_type)
            self.assert_template_used("errors/400.html")

    def test_scielo_php_with_sci_issues_script_but_incorrect_pid_must_redirect_to_home(
        self,
    ):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = "?script=sci_issues&pid="
            response = self.client.get(
                url_for("main.router_legacy") + qs, follow_redirects=True
            )

            # then
            self.assertStatus(response, 400)
            self.assertEqual("text/html; charset=utf-8", response.content_type)
            self.assert_template_used("errors/400.html")

    def test_scielo_php_with_sci_pdf_script_but_incorrect_pid_must_redirect_to_home(
        self,
    ):
        """
        acessar a url: /scielo.php?script=sci_serial&pid=  (pid inválido) vai redirecionar para index
        """
        # with
        with current_app.app_context():
            # when
            qs = "?script=sci_pdf&pid="
            response = self.client.get(
                url_for("main.router_legacy") + qs, follow_redirects=True
            )

            # then
            self.assertStatus(response, 400)
            self.assertEqual("text/html; charset=utf-8", response.content_type)
            self.assert_template_used("errors/400.html")
