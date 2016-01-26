# coding: utf-8
import os
import logging.config
from flask import Flask
from flask_assets import Environment, Bundle
from flask_debugtoolbar import DebugToolbarExtension
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import flask_admin
from flask_mail import Mail
from flask_babelex import Babel
from flask_babelex import lazy_gettext

import errors
from opac_schema.v1.models import Collection, Sponsor, Journal, Issue, Article

assets = Environment()
toolbar = DebugToolbarExtension()
dbmongo = MongoEngine()
dbsql = SQLAlchemy()
mail = Mail()
babel = Babel()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'admin.login_view'

logging.config.fileConfig(os.path.join(os.path.dirname(
                          os.path.abspath(__file__)), '../config/logger.ini'))

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    app = Flask(__name__,
                static_url_path='/static',
                static_folder='static',
                instance_relative_config=True)

    # Configurações
    app.config.from_object('config.default')  # Configuração basica
    app.config.from_object(config_name)  # Configuração dependente do ambiente
    app.config.from_pyfile('config.py')  # Configuração local não versionada (chaves, segredos, senhas etc.)

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
    # i18n
    babel.init_app(app)
    # login
    login_manager.init_app(app)
    # Toolbar
    toolbar.init_app(app)
    # Mongo
    dbmongo.init_app(app)
    # SQLAlchemy
    dbsql.init_app(app)
    # Emails
    mail.init_app(app)

    # Handler de páginas de erro
    errors.register_errorhandlers(app)

    # Interface do admin
    from .models import User
    from app.admin import views

    admin = flask_admin.Admin(
        app, 'OPAC admin',
        index_view=views.AdminIndexView(),
        template_mode='bootstrap3',
        base_template="admin/opac_base.html")

    admin.add_view(views.CollectionAdminView(Collection, name=lazy_gettext(u'Coleção')))
    admin.add_view(views.SponsorAdminView(Sponsor, name=lazy_gettext(u'Financiador')))
    admin.add_view(views.JournalAdminView(Journal, name=lazy_gettext(u'Periódico')))
    admin.add_view(views.IssueAdminView(Issue, name=lazy_gettext(u'Fascículo')))
    admin.add_view(views.ArticleAdminView(Article, name=lazy_gettext(u'Artigo')))
    admin.add_view(views.UserAdminView(User, dbsql.session, name=lazy_gettext(u'Usuário')))

    from .main import main as main_bp
    app.register_blueprint(main_bp)

    return app
