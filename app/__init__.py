# coding: utf-8
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__, static_url_path='/static', static_folder='static')

assets = Environment(app)

js = Bundle('js/vendor/jquery-1.11.0.min.js',
            'js/vendor/bootstrap.min.js',
            'js/vendor/jquery-ui.min.js',
            'js/plugins.js',
            'js/main.js',
            filters='jsmin', output='js/bundle.js')

css = Bundle('css/bootstrap.min.css',
             'css/scielo-portal.css',
             filters='cssmin',
             output='css/bundle.css')

assets.register('js_all', js)
assets.register('css_all', css)

# the toolbar is only enabled in debug mode:
app.debug = False

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'scielo'
app.config['ASSETS_DEBUG'] = False
# app.config.from_pyfile('mongodb.cfg')
app.config['MONGODB_SETTINGS'] = {
    'db': 'manager2mongo',
    # 'host': '192.168.1.35',
    # 'port': 12345
}
toolbar = DebugToolbarExtension(app)

db = MongoEngine(app)
from app import views
