# coding: utf-8

from flask import current_app, url_for

from . import utils
from .base import BaseTestCase


class HomeTestCase(BaseTestCase):
    def test_collection_trans_home(self):
        """
        Verificamos se a home esta com as traduções corretas para o nome da
        coleção.
        """

        with current_app.app_context():
            utils.makeOneCollection(
                {
                    "name_pt": "coleção falsa",
                    "name_es": "colección falsa",
                    "name_en": "dummy collection",
                }
            )

            with self.client as c:
                # idioma em 'pt_br'
                response = c.get(
                    url_for("main.set_locale", lang_code="pt_BR"),
                    headers={"Referer": "/"},
                    follow_redirects=True,
                )

                self.assertStatus(response, 200)
                expected_anchor = "coleção falsa"
                self.assertIn(expected_anchor, response.data.decode("utf-8"))

                # idioma em 'en'
                response = c.get(
                    url_for("main.set_locale", lang_code="en"),
                    headers={"Referer": "/"},
                    follow_redirects=True,
                )

                self.assertStatus(response, 200)
                expected_anchor = "dummy collection"
                self.assertIn(expected_anchor, response.data.decode("utf-8"))

                # idioma em 'es'
                response = c.get(
                    url_for("main.set_locale", lang_code="es"),
                    headers={"Referer": "/"},
                    follow_redirects=True,
                )

                self.assertStatus(response, 200)
                expected_anchor = "colección falsa"
                self.assertIn(expected_anchor, response.data.decode("utf-8"))
