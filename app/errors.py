# coding: utf-8
from flask import render_template


# Get solution from StackOverflow:
# http://stackoverflow.com/questions/30108000/flask-register-blueprint-error-python
def register_errorhandlers(app):

    def render_error(error):
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code

    for errcode in [500, 404, 403]:
        app.errorhandler(errcode)(render_error)
    return None
