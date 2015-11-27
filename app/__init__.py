# coding: utf-8
import os
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__,
            static_url_path='/static',
            static_folder='static',
            instance_relative_config=True)

# Config
app.config.from_object('config.default')  # Get all basic configuration
app.config.from_object(os.environ['OPAC_CONFIG'])  # Get enviroment configuration
app.config.from_pyfile('config.py')  # Get unversioned secret keys

# Assets
assets = Environment(app)

js = Bundle('js/vendor/jquery-1.11.0.min.js',
            'js/vendor/bootstrap.min.js',
            'js/vendor/jquery-ui.min.js',
            'js/plugins.js',
            'js/main.js',
            filters='jsmin', output='js/bundle.js')

css = Bundle('css/bootstrap.min.css',
             'css/scielo-portal.css',
             filters='cssmin', output='css/bundle.css')

assets.register('js_all', js)
assets.register('css_all', css)

# Toolbar
toolbar = DebugToolbarExtension(app)

# Mongo
db = MongoEngine(app)

from app import views
