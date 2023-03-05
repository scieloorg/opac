# coding: utf-8

import traceback

from flask import abort, current_app
from flask_babelex import lazy_gettext as __

from .base import BaseTestCase

ERROR_MSG = __("Mensagem de erro explicativo para o usuário")


class ErrorsTestCase(BaseTestCase):
    def _silence_traceback_print_exception(self):
        """
        Redefine a função encarregada para imprimir
        o stack trace, "silenciando" quando cualquer exeção levantada.
        No caso de querer gerer uma Exception intencionalmente (erro http 500)
        não é muito util ter o strack trace entre os resultados dos unittest.

        Para rastaurar ao comportamento habitual, deve invocar:
        ``self._restore_default_print_exception``
        """

        self._previous_propagate_exceptions = current_app.config["PROPAGATE_EXCEPTIONS"]
        current_app.config["PROPAGATE_EXCEPTIONS"] = False

        self._previous_print_stack = traceback.print_exception
        traceback.print_exception = lambda *args: None

    def _restore_traceback_print_exception(self):
        """
        Redefine a função encarregada para imprimir
        o stack trace, deixando que imprima o stack trace de qualquer exceção no test
        """
        current_app.config["PROPAGATE_EXCEPTIONS"] = True

        if self._previous_print_stack:
            traceback.print_exception = self._previous_print_stack

    @current_app.route("/bad_request")
    def bad_request():  # pylint:disable=no-method-argument
        abort(400, ERROR_MSG)

    @current_app.route("/forbidden")
    def forbidden_page():  # pylint:disable=no-method-argument
        abort(403, ERROR_MSG)

    @current_app.route("/page_not_found")
    def page_not_found():  # pylint:disable=no-method-argument
        abort(404, ERROR_MSG)

    @current_app.route("/internal_server_error")
    def internal_server_error():  # pylint:disable=no-method-argument
        raise Exception("intentional")

    def test_bad_request(self):
        response = self.client.get("/bad_request")
        self.assert_400(response)
        self.assertEqual("text/html; charset=utf-8", response.content_type)
        self.assert_template_used("errors/400.html")
        context_msg = self.get_context_variable("message")
        expected_msg = "<p>%s</p>" % ERROR_MSG
        self.assertEqual(expected_msg, context_msg)

    def test_bad_request_json(self):
        response = self.client.get(
            "/bad_request", headers={"Accept": "application/json"}
        )
        self.assert_400(response)
        self.assertEqual("application/json", response.content_type)
        self.assertIsNotNone(response.json)
        self.assertIn("error", list(response.json.keys()))
        json_msg = response.json["error"]
        expected_msg = "<p>%s</p>" % ERROR_MSG
        self.assertEqual(expected_msg, json_msg)

    def test_forbidden(self):
        response = self.client.get("/forbidden")
        self.assert_403(response)
        self.assertEqual("text/html; charset=utf-8", response.content_type)
        self.assert_template_used("errors/403.html")
        context_msg = self.get_context_variable("message")
        expected_msg = "<p>%s</p>" % ERROR_MSG
        self.assertEqual(expected_msg, context_msg)

    def test_forbidden_json(self):
        response = self.client.get("/forbidden", headers={"Accept": "application/json"})
        self.assert_403(response)
        self.assertEqual("application/json", response.content_type)
        self.assertIsNotNone(response.json)
        self.assertIn("error", list(response.json.keys()))
        json_msg = response.json["error"]
        expected_msg = "<p>%s</p>" % ERROR_MSG
        self.assertEqual(expected_msg, json_msg)

    def test_page_not_found(self):
        response = self.client.get("/page_not_found")
        self.assert_404(response)
        self.assertEqual("text/html; charset=utf-8", response.content_type)
        self.assert_template_used("errors/404.html")
        context_msg = self.get_context_variable("message")
        expected_msg = "<p>%s</p>" % ERROR_MSG
        self.assertEqual(expected_msg, context_msg)

    def test_page_not_found_json(self):
        response = self.client.get(
            "/page_not_found", headers={"Accept": "application/json"}
        )
        self.assert_404(response)
        self.assertEqual("application/json", response.content_type)
        self.assertIsNotNone(response.json)
        self.assertIn("error", list(response.json.keys()))
        json_msg = response.json["error"]
        expected_msg = "<p>%s</p>" % ERROR_MSG
        self.assertEqual(expected_msg, json_msg)

    def test_internal_server_error(self):
        current_app.config["DEBUG"] = False
        # silenciamos a impressão de exceções no console
        self._silence_traceback_print_exception()
        response = self.client.get("/internal_server_error")
        self.assert_500(response)
        # reativamos a impressão de exceções no console
        self._restore_traceback_print_exception()
        self.assertEqual("text/html; charset=utf-8", response.content_type)
        self.assert_template_used("errors/500.html")

    def test_internal_server_error_json(self):
        current_app.config["DEBUG"] = False
        # silenciamos a impressão de exceções no console
        self._silence_traceback_print_exception()
        response = self.client.get(
            "/internal_server_error", headers={"Accept": "application/json"}
        )
        self.assert_500(response)
        # reativamos a impressão de exceções no console
        self._restore_traceback_print_exception()
        self.assertEqual("application/json", response.content_type)
        self.assertEqual(response.json, {"error": "internal server error"})
