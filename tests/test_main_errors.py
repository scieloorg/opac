# coding: utf-8

from flask.ext.testing import TestCase
from flask import current_app, abort
from app import dbsql


class ErrorsTestCase(TestCase):

    def setUp(self):
        dbsql.create_all()

    def create_app(self):
        return current_app

    def tearDown(self):
        dbsql.session.remove()
        dbsql.drop_all()

    @current_app.route('/forbidden')
    def forbidden_page():
        abort(403)

    @current_app.route('/page_not_found')
    def page_not_found():
        abort(404)

    @current_app.route('/internal_server_error')
    def internal_server_error():
        1 // 0

    def test_forbidden(self):
        response = self.client.get('/forbidden')
        self.assert_403(response)
        self.assertEqual('text/html; charset=utf-8', response.content_type)
        self.assert_template_used("errors/403.html")

    def test_page_not_found(self):
        response = self.client.get('/page_not_found')
        self.assert_404(response)
        self.assertEqual('text/html; charset=utf-8', response.content_type)
        self.assert_template_used("errors/404.html")

    def test_internal_server_error(self):
        current_app.config['DEBUG'] = False
        current_app.config['PROPAGATE_EXCEPTIONS'] = False
        response = self.client.get('/internal_server_error')
        self.assert_500(response)
        self.assertEqual('text/html; charset=utf-8', response.content_type)
        self.assert_template_used("errors/500.html")
