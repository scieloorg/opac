# coding: utf-8

from flask import url_for, current_app
from flask_babelex import lazy_gettext as __

from .base import BaseTestCase
from . import utils


class MenuTestCase(BaseTestCase):

    # Collection Menu

    def test_alpha_link_is_selected_for_list_alpha(self):
        """
        Verficamos que o link do menú "Alfabética" tem o css:
        "selected" quando acessamos a view "collection_list_alpha"
        """
        response = self.client.get(url_for('main.collection_list'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_journal.html')
        expected_anchor = '<a href="/journals/#alpha" class="tab_link">\n              Lista alfab\xe9tica de peri\xf3dicos\n            </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_theme_link_is_selected_for_list_theme(self):
        """
        Verficamos que o link do menú "Temática" tem o css:
        "selected" quando acessamos a view "collection_list_theme"
        """
        response = self.client.get(url_for('main.collection_list'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_journal.html')
        expected_anchor = '<a href="/journals/#theme" class="tab_link">\n              Lista temática de periódicos\n            </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    # def test_institution_link_is_selected_for_list_institution(self):
    #     """
    #     Verficamos que o link do menú "Por instituição" tem o css:
    #     "selected" quando acessamos a view "collection_list_institution"
    #     """
    #     response = self.client.get(url_for('main.collection_list'))

    #     self.assertStatus(response, 200)
    #     self.assertTemplateUsed('collection/list_journal.html')
    #     expected_anchor = '<a href="/journals/#publisher" class="tab_link">\n              Lista de periódicos por editoras\n            </a>'
    #     self.assertIn(expected_anchor, response.data.decode('utf-8'))

    # Hamburger Menu
    def test_links_in_hamburger_menu(self):
        """
        no menú de hamurger, verificamos os links que apontam a views do opac
        """
        with current_app.app_context():
            collection = utils.makeOneCollection({'name': 'dummy collection'})

            with self.client as c:

                response = c.get(url_for('main.index'))
                response_data = response.data.decode('utf-8')
                self.assertStatus(response, 200)
                expected_anchor1 = """<a href="%s">\n        <strong>%s</strong>""" % (url_for('.index'), collection.name or __('NOME DA COLEÇÃO!!'))
                self.assertIn(expected_anchor1, response_data)
                expected_anchor2 = """<li>\n            <a href="%s" class="tab_link">\n              %s\n            </a>\n          </li>""" % (url_for('.collection_list') + '#alpha', __('Lista alfabética de periódicos'))
                self.assertIn(expected_anchor2, response_data)
                expected_anchor3 = """<li>\n            <a href="%s" class="tab_link">\n              %s\n            </a>\n          </li>""" % (url_for('.collection_list') + '#theme', __('Lista temática de periódicos'))
                self.assertIn(expected_anchor3, response_data)
                # expected_anchor4 = """<li>\n            <a href="%s" class="tab_link">\n              %s\n            </a>\n          </li>""" % (url_for('.collection_list') + '#publisher', __('Lista de periódicos por editoras'))
                # self.assertIn(expected_anchor4, response_data)
                expected_anchor5 = """<li>\n            <a href="%s">\n              %s\n            </a>\n          </li>""" % (current_app.config['URL_SEARCH'] + "?q=*&lang=pt&filter[in][]=" + current_app.config['OPAC_COLLECTION'], 'Busca')
                self.assertIn(expected_anchor5, response_data)
                expected_anchor6 = """<li>\n            <a target="_blank" href="%s/?collection=%s">\n              %s\n            </a>\n          </li>\n          <li>""" % (current_app.config['METRICS_URL'], current_app.config['OPAC_COLLECTION'], __('M\xe9tricas'))
                self.assertIn(expected_anchor6, response_data)
                expected_anchor7 = """<a href="%s" class="onlineSubmission">\n      <span class="glyphBtn infoMenu"></span>\n      %s %s\n    </a>""" % (url_for('.about_collection'), __('Sobre o SciELO'), collection.name)
                self.assertIn(expected_anchor7, response_data)
                expected_anchor8 = """<li>\n            <a href="/collection/about/">\n              %s\n            </a>\n          </li>""" % __('Contatos')
                self.assertIn(expected_anchor8, response_data)
                expected_anchor9 = """<a href="#">\n        <strong>SciELO.org - %s</strong>\n      </a>""" % __('Rede SciELO')
                self.assertIn(expected_anchor9, response_data)
                # rede/scielo org
                expected_anchor10 = """<li>\n          <a href="http://www.scielo.org/php/index.php">\n            %s\n          </a>\n        </li>""" % __('Coleções nacionais e temáticas')
                self.assertIn(expected_anchor10, response_data)
                expected_anchor11 = """<li>\n          <a href="http://www.scielo.org/applications/scielo-org/php/secondLevel.php?xml=secondLevelForAlphabeticList&xsl=secondLevelForAlphabeticList">\n            %s\n          </a>\n        </li>""" % __('Lista alfabética de periódicos')
                self.assertIn(expected_anchor11, response_data)
                expected_anchor12 = """<li>\n          <a href="http://www.scielo.org/applications/scielo-org/php/secondLevel.php?xml=secondLevelForSubjectByLetter&xsl=secondLevelForSubjectByLetter">\n            %s\n          </a>\n        </li>""" % __('Lista de periódicos por assunto')
                self.assertIn(expected_anchor12, response_data)
                expected_anchor13 = """<li>\n          <a href="%s">\n            %s\n          </a>\n        </li>""" % (current_app.config['URL_SEARCH'], 'Busca')
                self.assertIn(expected_anchor13, response_data)
                expected_anchor14 = """<li>\n            <a target="_blank" href="%s/?collection=%s">\n              %s\n            </a>\n          </li>""" % (current_app.config['METRICS_URL'], current_app.config['OPAC_COLLECTION'], 'Métricas')
                self.assertIn(expected_anchor14, response_data)
                expected_anchor15 = """<li>\n          <a href="http://www.scielo.org/php/level.php?lang=pt&component=56&item=9">\n            %s\n          </a>\n        </li>""" % __('Acesso OAI e RSS')
                self.assertIn(expected_anchor15, response_data)
                expected_anchor16 = """<li>\n          <a href="http://www.scielo.org/php/level.php?lang=pt&component=56&item=8">\n            %s\n          </a>\n        </li>""" % __('Sobre a Rede SciELO')
                self.assertIn(expected_anchor16, response_data)
                expected_anchor17 = """<li>\n          <a href="#">\n            %s\n          </a>\n        </li>""" % __('Contatos')
                self.assertIn(expected_anchor17, response_data)
                # expected_anchor18 = u"""<li>\n      <a href="#"><strong>%s</strong></a>\n    </li>""" % __(u'Portal do Autor')
                # self.assertIn(expected_anchor18, response_data)

    def test_blog_link_in_hamburger_menu(self):
        """
        Verificamos que o link para o blog em perspectiva fique
        apontando ao link certo considerando o idioma da sessão
        """

        with current_app.app_context():
            utils.makeOneCollection({'name': 'dummy collection'})
            with self.client as c:
                # idioma em 'pt_br'
                response = c.get(
                    url_for('main.set_locale', lang_code='pt_BR'),
                    headers={'Referer': '/'},
                    follow_redirects=True)

                self.assertStatus(response, 200)
                expected_anchor = '<a href="http://blog.scielo.org/">'
                self.assertIn(expected_anchor, response.data.decode('utf-8'))

                # idioma em 'en'
                response = c.get(
                    url_for('main.set_locale', lang_code='en'),
                    headers={'Referer': '/'},
                    follow_redirects=True)

                self.assertStatus(response, 200)
                expected_anchor = '<a href="http://blog.scielo.org/en/">'
                self.assertIn(expected_anchor, response.data.decode('utf-8'))

                # idioma em 'es'
                response = c.get(
                    url_for('main.set_locale', lang_code='es'),
                    headers={'Referer': '/'},
                    follow_redirects=True)

                self.assertStatus(response, 200)
                expected_anchor = '<a href="http://blog.scielo.org/es/">'
                self.assertIn(expected_anchor, response.data.decode('utf-8'))

    # Journal Menu
    def test_journal_detail_menu(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``journal/detail.html``
        """
        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            utils.makeOneIssue({
                'journal': journal,
                'year': '2016', 'volume': '1',
                'number': '1', 'order': '1',
            })

            issue2 = utils.makeOneIssue({
                'journal': journal,
                'year': '2016', 'volume': '1',
                'number': '2', 'order': '2',
            })
            issue3 = utils.makeOneIssue({
                'journal': journal,
                'year': '2016', 'volume': '1',
                'number': '3', 'order': '3',
            })

            response = self.client .get(
                url_for('main.journal_detail', url_seg=journal.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('journal/detail.html')

            expect_btn_anterior = '<a href="%s" class="btn group ">\n          &laquo; número anterior\n        </a>' % url_for('.issue_toc', url_seg=journal.url_segment, url_seg_issue=issue2.url_segment)

            expect_btn_atual = '<a href="%s" class="btn group  ">\n          número atual\n        </a>' % url_for('.issue_toc', url_seg=journal.url_segment, url_seg_issue=issue3.url_segment)

            expect_btn_proximo = '<a href="" class="btn group  disabled ">\n          número seguinte &raquo;\n        </a>'

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))

    def test_journal_detail_menu_without_issues(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``jorunal/detail.html`` quando o periódico
        não tem número.
        """
        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            response = self.client.get(url_for('main.journal_detail',
                                       url_seg=journal.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('journal/detail.html')

            expect_btn_anterior = '<a href="/journal_acron//" class="btn group  disabled ">\n          &laquo; número anterior\n        </a>'

            expect_btn_atual = '<a href="/journal_acron//" class="btn group   disabled ">\n          número atual\n        </a>'

            expect_btn_proximo = '<a href="" class="btn group  disabled ">\n          número seguinte &raquo;\n        </a>'

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            response_data = response.data.decode('utf-8')
            for btn in expected_btns:
                self.assertIn(btn, response_data)

    def test_journal_detail_menu_with_one_issue(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``jorunal/detail.html`` quando o periódico
        tem um número o botão ``próximo`` e ``anterior`` deve vir desabilitados.
        """
        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            issue = utils.makeOneIssue({
                'journal': journal,
                'year': '2016', 'volume': '1',
                'number': '1', 'order': '1',
            })

            response = self.client.get(url_for('main.journal_detail',
                                       url_seg=journal.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('journal/detail.html')
            expect_btn_anterior = '<a href="/journal_acron//" class="btn group  disabled ">\n          &laquo; número anterior\n        </a>'

            expect_btn_atual = '<a href="%s" class="btn group  ">\n          número atual\n        </a>' % url_for('.issue_toc', url_seg=journal.url_segment, url_seg_issue=issue.url_segment)

            expect_btn_proximo = '<a href="" class="btn group  disabled ">\n          número seguinte &raquo;\n        </a>'

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            response_data = response.data.decode('utf-8')
            for btn in expected_btns:
                self.assertIn(btn, response_data)

    def test_journal_detail_menu_access_issue_toc_on_any_issue(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``jorunal/detail.html``, quando acessamos
        qualquer número.
        """

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue1 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '1', 'order': '1', })
            issue2 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '2', 'order': '2', })
            issue3 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '3', 'order': '3', })

            issue_toc_url = url_for(
                'main.issue_toc',
                url_seg=journal.url_segment,
                url_seg_issue=issue2.url_segment)

            response = self.client .get(issue_toc_url)

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/toc.html')

            expect_btn_anterior = '<a href="%s" class="btn group ">\n          &laquo; número anterior\n        </a>' % url_for('.issue_toc', url_seg=journal.url_segment, url_seg_issue=issue1.url_segment)

            expect_btn_atual = '<a href="%s" class="btn group  ">\n          número atual\n        </a>' % url_for('.issue_toc', url_seg=journal.url_segment, url_seg_issue=issue3.url_segment)

            expect_btn_proximo = '<a href="%s" class="btn group ">\n          número seguinte &raquo;\n        </a>' % url_for('.issue_toc', url_seg=journal.url_segment, url_seg_issue=issue3.url_segment)

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            response_data = response.data.decode('utf-8')
            for btn in expected_btns:
                self.assertIn(btn, response_data)

    def test_journal_detail_menu_access_issue_toc_lastest_issue(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``jorunal/detail.html``, quando acessamos
        o número mais recente.
        """
        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            utils.makeOneIssue({
                'journal': journal,
                'year': '2016', 'volume': '1',
                'number': '1', 'order': '1',
            })

            issue2 = utils.makeOneIssue({
                'journal': journal,
                'year': '2016', 'volume': '1',
                'number': '2', 'order': '2'
            })

            issue3 = utils.makeOneIssue({
                'journal': journal,
                'year': '2016', 'volume': '1',
                'number': '3', 'order': '3'
            })

            issue_toc_url = url_for(
                'main.issue_toc',
                url_seg=journal.url_segment,
                url_seg_issue=issue3.url_segment)

            response = self.client.get(issue_toc_url)
            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/toc.html')

            expect_btn_anterior = '<a href="%s" class="btn group ">\n          &laquo; número anterior\n        </a>' % url_for('.issue_toc', url_seg=journal.url_segment, url_seg_issue=issue2.url_segment)

            expect_btn_atual = '<a href="%s" class="btn group  selected  ">\n          número atual\n        </a>' % url_for('.issue_toc', url_seg=journal.url_segment, url_seg_issue=issue3.url_segment)

            expect_btn_proximo = '<a href="" class="btn group  disabled ">\n          número seguinte &raquo;\n        </a>'

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))

    def test_journal_detail_menu_access_issue_toc_oldest_issue(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``jorunal/detail.html``, quando acessamos
        o número mais antigo.
        """
        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            issue1 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '1', 'order': '1', })
            issue2 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '2', 'order': '2', })
            issue3 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '3', 'order': '3', })

            response = self.client.get(url_for('main.issue_toc',
                                       url_seg=journal.url_segment,
                                       url_seg_issue=issue1.url_segment))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/toc.html')

            expect_btn_anterior = '<a href="/journal_acron//" class="btn group  disabled ">\n          &laquo; número anterior\n        </a>'

            expect_btn_atual = '<a href="%s" class="btn group  ">\n          número atual\n        </a>' % url_for('.issue_toc', url_seg=journal.url_segment, url_seg_issue=issue3.url_segment)

            expect_btn_proximo = '<a href="%s" class="btn group ">\n          número seguinte &raquo;\n        </a>' % url_for('.issue_toc', url_seg=journal.url_segment, url_seg_issue=issue2.url_segment)

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))

    # Article Menu
    def test_article_detail_menu(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``article/detail.html``.
        """

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            journal = utils.makeOneJournal()

            issue = utils.makeOneIssue({
                'journal': journal,
                'year': '2016',
                'volume': '1',
                'number': '1',
                'order': '1',
            })

            article1 = utils.makeOneArticle({
                'issue': issue,
                'order': 1,
                'elocation': 'e1234560'
            })

            article2 = utils.makeOneArticle({
                'issue': issue,
                'order': 2,
                'elocation': 'e1234561'
            })

            article3 = utils.makeOneArticle({
                'issue': issue,
                'order': 3,
                'elocation': 'e1234562'
            })

            article_detail_url = url_for(
                'main.article_detail',
                url_seg=journal.url_segment,
                url_seg_issue=issue.url_segment,
                url_seg_article=article2.url_segment)

            response = self.client.get(article_detail_url)

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')

            expect_btn_anterior = '<a href="%s" class="btn group ">\n                    &laquo; artigo anterior\n                </a>' % url_for(
                '.article_detail',
                url_seg=journal.url_segment,
                url_seg_issue=issue.url_segment,
                url_seg_article=article1.url_segment)

            expect_btn_atual = '<a href="" class="btn group disabled">\n                    artigo atual\n                </a>'

            expect_btn_proximo = '<a href="%s" class="btn group ">\n                    artigo seguinte &raquo;\n                </a>' % url_for(
                '.article_detail',
                url_seg=journal.url_segment,
                url_seg_issue=issue.url_segment,
                url_seg_article=article3.url_segment)

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))

    def test_article_detail_menu_when_last_article(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``article/detail.html`` quando é o
        último artigo. O botão próximo deve esta desativado.
        """

        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            issue = utils.makeOneIssue({
                'journal': journal,
                'year': '2016',
                'volume': '1',
                'number': '1',
                'order': '1'
            })

            utils.makeOneArticle({
                'issue': issue,
                'order': 1,
                'elocation': 'e1234562'
            })

            article2 = utils.makeOneArticle({
                'issue': issue,
                'order': 2,
                'elocation': 'e1234562'
            })

            article3 = utils.makeOneArticle({
                'issue': issue,
                'order': 3,
                'elocation': 'e1234562'
            })

            article_detail_url = url_for(
                'main.article_detail',
                url_seg=journal.url_segment,
                url_seg_issue=issue.url_segment,
                url_seg_article=article3.url_segment)

            response = self.client.get(article_detail_url)

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')

            expect_btn_anterior = '<a href="/journal_acron/2016.v1n1supplX//" class="btn group  disabled ">\n                    &laquo; artigo anterior\n                </a>'

            expect_btn_atual = '<a href="" class="btn group disabled">\n                    artigo atual\n                </a>'

            expect_btn_proximo = '<a href="%s" class="btn group ">\n                    artigo seguinte &raquo;\n                </a>' % url_for(
                '.article_detail',
                url_seg=journal.url_segment,
                url_seg_issue=issue.url_segment,
                url_seg_article=article2.url_segment)

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))

    def test_article_detail_menu_when_first_article(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``article/detail.html`` quando é o
        primeiro artigo. O botão anterior deve esta desativado.
        """

        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            utils.makeOneCollection()

            issue = utils.makeOneIssue({
                'journal': journal,
                'year': '2016', 'volume': '1',
                'number': '1', 'order': '1'
            })

            article1 = utils.makeOneArticle({
                'issue': issue,
                'order': 1,
                'elocation': 'e1234562'
            })

            article2 = utils.makeOneArticle({
                'issue': issue,
                'order': 2,
                'elocation': 'e1234562'
            })

            utils.makeOneArticle({
                'issue': issue,
                'order': 3,
                'elocation': 'e1234562'
            })

            article_detail_url = url_for(
                'main.article_detail',
                url_seg=journal.url_segment,
                url_seg_issue=issue.url_segment,
                url_seg_article=article1.url_segment)

            response = self.client.get(article_detail_url)

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')

            expect_btn_anterior = '<a href="/journal_acron/2016.v1n1supplX//" class="btn group  disabled ">\n                    &laquo; artigo anterior\n                </a>'

            expect_btn_atual = '<a href="" class="btn group disabled">\n                    artigo atual\n                </a>'

            expect_btn_proximo = '<a href="%s" class="btn group ">\n                    artigo seguinte &raquo;\n                </a>' % url_for(
                '.article_detail',
                url_seg=journal.url_segment,
                url_seg_issue=issue.url_segment,
                url_seg_article=article2.url_segment)

            expected_btns = [
                expect_btn_anterior,
                expect_btn_atual,
                expect_btn_proximo
            ]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))
