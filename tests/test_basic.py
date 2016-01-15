from flask.ext.testing import TestCase
from flask import current_app
from app import dbsql


class BasicsTestCase(TestCase):
    def setUp(self):
        # criamos o banco de dados relacional
        dbsql.create_all()

    def create_app(self):
        return current_app

    def tearDown(self):
        # apagamos o banco de dados relacional
        dbsql.session.remove()
        dbsql.drop_all()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertFalse(current_app.config['TESTING'])
