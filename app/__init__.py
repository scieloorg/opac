# coding: utf-8
import os
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import flask_admin

from app.admin.views import AdminIndexView

assets = Environment()
toolbar = DebugToolbarExtension()
dbmongo = MongoEngine()
dbsql = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'admin.login_view'


def create_app(config_name=None):
    app = Flask(__name__,
                static_url_path='/static',
                static_folder='static',
                instance_relative_config=True)
    # Config
    app.config.from_object('config.default')  # Get all basic configuration
    app.config.from_object(config_name)  # Get enviroment configuration
    app.config.from_pyfile('config.py')  # Get unversioned secret keys

    # Assets
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
    assets.init_app(app)

    # login
    login_manager.init_app(app)
    # Toolbar
    toolbar.init_app(app)
    # Mongo
    dbmongo.init_app(app)
    # SQLAlchemy
    dbsql.init_app(app)
    # Admin
    admin = flask_admin.Admin(app, 'OPAC admin', index_view=AdminIndexView(), template_mode='bootstrap3')

    from .main import main as main_bp
    app.register_blueprint(main_bp)

    return app
