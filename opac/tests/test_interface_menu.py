# coding: utf-8

from flask import url_for
from flask import Flask, url_for, current_app

from base import BaseTestCase
import utils


class MenuTestCase(BaseTestCase):

    # Collection Menu
    def test_home_link_is_selected_for_index_view(self):
        """
        Verficamos que o link do menú "Home" tem o css:
        "selected" quando acessamos a view "index"
        """
        response = self.client.get(url_for('main.index'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/index.html')
        expected_anchor = u'<a href="/"\n         class="btn single selected">\n        <span class="glyphBtn home"></span> Home\n      </a>'
        # expected_anchor = u'<a class="btn single " href="/"><span class="glyphBtn home"></span> Home </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_search_link_is_selected_for_search_view(self):
        """
        Verficamos que o link do menú "Buscar artigos" tem o css:
        "selected" quando acessamos a view "search"
        """
        response = self.client.get(url_for('main.search'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/search.html')
        expected_anchor = u'<a href="/search"\n         class="btn single selected">\n        <span class="glyphBtn search"></span>\n        <span class="hidden-sm">Buscar artigos</span>\n        <span class="hidden-md hidden-lg">Buscar</span>\n      </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_alpha_link_is_selected_for_list_alpha(self):
        """
        Verficamos que o link do menú "Alfabética" tem o css:
        "selected" quando acessamos a view "collection_list_alpha"
        """
        response = self.client.get(url_for('main.collection_list_alpha'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_alpha.html')
        expected_anchor = u'<a href="/journals"\n             class="btn group selected">\n            Alfabética\n          </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_theme_link_is_selected_for_list_theme(self):
        """
        Verficamos que o link do menú "Temática" tem o css:
        "selected" quando acessamos a view "collection_list_theme"
        """
        response = self.client.get(url_for('main.collection_list_theme'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_theme.html')
        expected_anchor = u'<a href="/journals/theme"\n             class="btn group selected">\n            Temática\n          </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_institution_link_is_selected_for_list_institution(self):
        """
        Verficamos que o link do menú "Por instituição" tem o css:
        "selected" quando acessamos a view "collection_list_institution"
        """
        response = self.client.get(url_for('main.collection_list_institution'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/list_institution.html')
        expected_anchor = u'<a href="/journals/institution"\n             class="btn group selected">\n            Por instituição\n          </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_metrics_link_is_selected_for_metric_view(self):
        """
        Verficamos que o link do menú "Métricas" tem o css:
        "selected" quando acessamos a view "metrics"
        """
        response = self.client.get(url_for('main.metrics'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/metrics.html')
        expected_anchor = u'<a href="/metrics"\n         class="btn single selected">\n        <span class="glyphBtn metrics"></span> Métricas\n      </a>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    def test_about_link_is_selected_for_about_view(self):
        """
        Verficamos que o link do menú "Sobre o Scielo" tem o css:
        "selected" quando acessamos a view "about"
        """
        response = self.client.get(url_for('main.about'))

        self.assertStatus(response, 200)
        self.assertTemplateUsed('collection/about.html')
        expected_anchor = u'<a href="/about"\n         class="btn single dropdown-toggle selected">\n        <span class="glyphBtn infoMenu"></span>\n        <span class="hidden-sm">Sobre o SciELO</span>'
        self.assertIn(expected_anchor, response.data.decode('utf-8'))

    # Hamburger Menu
    def test_links_in_hamburger_menu(self):
        """
        no menú de hamurger, verificamos os links que apontam a views do opac
        """
        response = self.client.get(url_for('main.index'))
        self.assertStatus(response, 200)
        expected_anchor1 = u"""<a href="%s"><strong>SciELO Brasil</strong></a>""" % url_for('.index')
        self.assertIn(expected_anchor1, response.data.decode('utf-8'))
        expected_anchor2 = u"""<li><a href="%s">Lista alfabética de periódicos</a></li>""" % url_for('.collection_list_alpha')
        self.assertIn(expected_anchor2, response.data.decode('utf-8'))
        expected_anchor3 = u"""<li><a href="%s">Lista temática de periódicos</a></li>""" % url_for('.collection_list_theme')
        self.assertIn(expected_anchor3, response.data.decode('utf-8'))
        expected_anchor4 = u"""<li><a href="%s">Busca</a></li>""" % url_for('.search')
        self.assertIn(expected_anchor4, response.data.decode('utf-8'))
        expected_anchor5 = u"""<li><a href="%s">Métricas</a></li>""" % url_for('.metrics')
        self.assertIn(expected_anchor5, response.data.decode('utf-8'))
        expected_anchor6 = u"""<li><a href="%s">Sobre o SciELO Brasil</a></li>""" % url_for('.about')
        self.assertIn(expected_anchor6, response.data.decode('utf-8'))
        expected_anchor7 = u"""<li><a href="#">Contatos</a></li>"""
        self.assertIn(expected_anchor7, response.data.decode('utf-8'))
        expected_anchor8 = u"""<a href="#"><strong>SciELO.org - Rede SciELO</strong></a>"""
        # rede/scielo org
        self.assertIn(expected_anchor8, response.data.decode('utf-8'))
        expected_anchor9 = u"""<li><a href="http://www.scielo.org/php/index.php">Coleções nacionais e temáticas</a></li>"""
        self.assertIn(expected_anchor9, response.data.decode('utf-8'))
        expected_anchor10 = u"""<li><a href="http://www.scielo.org/applications/scielo-org/php/secondLevel.php?xml=secondLevelForAlphabeticList&xsl=secondLevelForAlphabeticList">Lista alfabética de periódicos</a></li>"""
        self.assertIn(expected_anchor10, response.data.decode('utf-8'))
        expected_anchor11 = u"""<li><a href="http://www.scielo.org/applications/scielo-org/php/secondLevel.php?xml=secondLevelForSubjectByLetter&xsl=secondLevelForSubjectByLetter">Lista de periódicos por assunto</a></li>"""
        self.assertIn(expected_anchor11, response.data.decode('utf-8'))
        expected_anchor12 = u"""<li><a href="http://search.scielo.org/">Busca</a></li>"""
        self.assertIn(expected_anchor12, response.data.decode('utf-8'))
        expected_anchor13 = u"""<li><a href="http://www.scielo.org/applications/scielo-org/php/siteUsage.php">Métricas</a></li>"""
        self.assertIn(expected_anchor13, response.data.decode('utf-8'))
        expected_anchor14 = u"""<li><a href="http://www.scielo.org/php/level.php?lang=pt&component=56&item=9">Acesso OAI e RSS</a></li>"""
        self.assertIn(expected_anchor14, response.data.decode('utf-8'))
        expected_anchor15 = u"""<li><a href="http://www.scielo.org/php/level.php?lang=pt&component=56&item=8">Sobre a Rede SciELO</a></li>"""
        self.assertIn(expected_anchor15, response.data.decode('utf-8'))
        expected_anchor16 = u"""<li><a href="#">Contatos</a></li>"""
        self.assertIn(expected_anchor16, response.data.decode('utf-8'))
        expected_anchor17 = u"""<a href="#"><strong>Portal do Autor</strong></a>"""
        self.assertIn(expected_anchor17, response.data.decode('utf-8'))

    def test_blog_link_in_hamburger_menu(self):
        """
        Verificamos que o link para o blog em perspectiva fique
        apontando ao link certo considerando o idioma da sessão
        """
        with self.client as c:
            collection = utils.makeOneCollection()
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
            collection = utils.makeOneCollection()

            issue1 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '1', 'order': '1', })
            issue2 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '2', 'order': '2', })
            issue3 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '3', 'order': '3', })

            response = self.client .get(url_for('main.journal_detail',
                                     journal_id=journal.jid))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('journal/detail.html')

            expect_btn_anterior = u'<a href="%s" class="btn group ">\xab anterior</a>' % url_for('.issue_toc', issue_id=issue2.iid)

            expect_btn_atual = u'<a href="%s" class="btn group  ">atual</a>' % url_for('.issue_toc', issue_id=issue3.iid)

            expect_btn_proximo = u'<a href="/issues/" class="btn group  disabled ">pr\xf3ximo \xbb</a>'

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))

    def test_journal_detail_menu_without_issues(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``jorunal/detail.html`` quando o periódico
        não tem fascículo.
        """
        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            response = self.client.get(url_for('main.journal_detail',
                                       journal_id=journal.jid))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('journal/detail.html')
            expect_btn_anterior = u'<a href="/issues/" class="btn group  disabled ">\xab anterior</a>'

            expect_btn_atual = u'<a href="/issues/" class="btn group   disabled ">atual</a>'

            expect_btn_proximo = u'<a href="/issues/" class="btn group  disabled ">pr\xf3ximo \xbb</a>'

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))

    def test_journal_detail_menu_with_on_issue(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``jorunal/detail.html`` quando o periódico
        tem um fascículo o botão ``próximo`` e ``anterior`` deve vir desabilitados.
        """
        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '1', 'order': '1', })

            response = self.client.get(url_for('main.journal_detail',
                                       journal_id=journal.jid))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('journal/detail.html')
            expect_btn_anterior = u'<a href="/issues/" class="btn group  disabled ">\xab anterior</a>'

            expect_btn_atual = u'<a href="%s" class="btn group  ">atual</a>' % url_for('.issue_toc', issue_id=issue.iid)

            expect_btn_proximo = u'<a href="/issues/" class="btn group  disabled ">pr\xf3ximo \xbb</a>'

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))

    def test_journal_detail_menu_access_issue_toc_on_any_issue(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``jorunal/detail.html``, quando acessamos
        qualquer fascículo.
        """
        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            issue1 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '1', 'order': '1', })
            issue2 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '2', 'order': '2', })
            issue3 = utils.makeOneIssue({'journal': journal,
                                         'year': '2016', 'volume': '1',
                                         'number': '3', 'order': '3', })

            response = self.client .get(url_for('main.issue_toc',
                                        issue_id=issue2.iid))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/toc.html')

            expect_btn_anterior = u'<a href="%s" class="btn group ">\xab anterior</a>' % url_for('.issue_toc', issue_id=issue1.iid)

            expect_btn_atual = u'<a href="%s" class="btn group  ">atual</a>' % url_for('.issue_toc', issue_id=issue3.iid)

            expect_btn_proximo = u'<a href="%s" class="btn group ">pr\xf3ximo \xbb</a>' % url_for('.issue_toc', issue_id=issue3.iid)

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))

    def test_journal_detail_menu_access_issue_toc_lastest_issue(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``jorunal/detail.html``, quando acessamos
        o fascículo mais recente.
        """
        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

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
                                       issue_id=issue3.iid))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/toc.html')

            expect_btn_anterior = u'<a href="%s" class="btn group ">\xab anterior</a>' % url_for('.issue_toc', issue_id=issue2.iid)

            expect_btn_atual = u'<a href="%s" class="btn group  selected  ">atual</a>' % url_for('.issue_toc', issue_id=issue3.iid)

            expect_btn_proximo = u'<a href="/issues/" class="btn group  disabled ">pr\xf3ximo \xbb</a>'

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))

    def test_journal_detail_menu_access_issue_toc_oldest_issue(self):
        """
        Teste para verificar se os botões estão ``anterior``, ``atual``,
        ``próximo`` estão disponíveis no ``jorunal/detail.html``, quando acessamos
        o fascículo mais antigo.
        """
        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

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
                                       issue_id=issue1.iid))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('issue/toc.html')

            expect_btn_anterior = u'<a href="/issues/" class="btn group  disabled ">\xab anterior</a>'

            expect_btn_atual = u'<a href="%s" class="btn group  ">atual</a>' % url_for('.issue_toc', issue_id=issue3.iid)

            expect_btn_proximo = u'<a href="%s" class="btn group ">pr\xf3ximo \xbb</a>' % url_for('.issue_toc', issue_id=issue2.iid)

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

        journal = utils.makeOneJournal()

        with current_app.app_context():
            # Criando uma coleção para termos o objeto ``g`` na interface
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal,
                                        'year': '2016', 'volume': '1',
                                        'number': '1', 'order': '1', })

            resource = utils.makeOneResource()

            article1 = utils.makeOneArticle({'issue': issue, 'order': 1,
                                             'htmls': [resource]})
            article2 = utils.makeOneArticle({'issue': issue, 'order': 2,
                                             'htmls': [resource]})
            article3 = utils.makeOneArticle({'issue': issue, 'order': 3,
                                             'htmls': [resource]})

            response = self.client.get(url_for('main.article_detail',
                                               article_id=article2.aid))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')

            expect_btn_anterior = u'<a href="%s" class="btn group ">\xab anterior</a>' % url_for('.article_detail', article_id=article1.aid)

            expect_btn_atual = u'<a href="" class="btn group disabled">atual</a>'

            expect_btn_proximo = u'<a href="%s" class="btn group ">pr\xf3ximo \xbb</a>' % url_for('.article_detail', article_id=article3.aid)

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
            collection = utils.makeOneCollection()

            issue = utils.makeOneIssue({'journal': journal,
                                        'year': '2016', 'volume': '1',
                                        'number': '1', 'order': '1', })

            resource = utils.makeOneResource()

            article1 = utils.makeOneArticle({'issue': issue, 'order': 1,
                                             'htmls': [resource]})
            article2 = utils.makeOneArticle({'issue': issue, 'order': 2,
                                             'htmls': [resource]})
            article3 = utils.makeOneArticle({'issue': issue, 'order': 3,
                                             'htmls': [resource]})

            response = self.client.get(url_for('main.article_detail',
                                               article_id=article3.aid))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')

            expect_btn_anterior = u'<a href="%s" class="btn group ">\xab anterior</a>' % url_for('.article_detail', article_id=article2.aid)

            expect_btn_atual = u'<a href="" class="btn group disabled">atual</a>'

            expect_btn_proximo = u'<a href="/articles/" class="btn group  disabled ">pr\xf3ximo \xbb</a>'

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
            collection = utils.makeOneCollection()

            resource = utils.makeOneResource()

            issue = utils.makeOneIssue({'journal': journal,
                                        'year': '2016', 'volume': '1',
                                        'number': '1', 'order': '1', })

            article1 = utils.makeOneArticle({'issue': issue, 'order': 1,
                                             'htmls': [resource]})
            article2 = utils.makeOneArticle({'issue': issue, 'order': 2,
                                             'htmls': [resource]})
            article3 = utils.makeOneArticle({'issue': issue, 'order': 3,
                                             'htmls': [resource]})

            response = self.client.get(url_for('main.article_detail',
                                               article_id=article1.aid))

            self.assertStatus(response, 200)
            self.assertTemplateUsed('article/detail.html')

            expect_btn_anterior = u'<a href="/articles/" class="btn group  disabled ">\xab anterior</a>'

            expect_btn_atual = u'<a href="" class="btn group disabled">atual</a>'

            expect_btn_proximo = u'<a href="%s" class="btn group ">pr\xf3ximo \xbb</a>' % url_for('.article_detail', article_id=article2.aid)

            expected_btns = [expect_btn_anterior, expect_btn_atual, expect_btn_proximo]

            # Verificar se todos os btns do menu estão presentes no HTML da resposta
            for btn in expected_btns:
                self.assertIn(btn, response.data.decode('utf-8'))
