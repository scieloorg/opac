# coding: utf-8

from flask.ext.testing import TestCase
from flask import current_app, url_for
from app import create_app, dbsql, dbmongo

from base import MongoInstance, BaseTestCase


class FlaskClientTestCase(TestCase):
    def setUp(self):
        dbsql.create_all()

    def create_app(self):
        return current_app

    def tearDown(self):
        dbsql.session.remove()
        dbsql.drop_all()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertEqual(200, response.status_code)
        self.assertEqual('text/html; charset=utf-8', response.content_type)
        self.assert_template_used("collection/index.html")
