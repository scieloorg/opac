# coding: utf-8
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mongoengine import MongoEngine

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder='static')

# the toolbar is only enabled in debug mode:
app.debug = True

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'scielo'
# app.config.from_pyfile('mongodb.cfg')
app.config['MONGODB_SETTINGS'] = {
    'db': 'manager2mongo',
    # 'host': '192.168.1.35',
    # 'port': 12345
}
toolbar = DebugToolbarExtension(app)

db = MongoEngine(app)
from app import views
