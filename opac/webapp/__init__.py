# coding: utf-8
import os

from flask import Flask
from flask_assets import Environment, Bundle
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import flask_admin
from flask_mail import Mail
from flask_babelex import Babel
from flask_babelex import lazy_gettext
from werkzeug.contrib.fixers import ProxyFix

from opac_schema.v1.models import Collection, Sponsor, Journal, Issue, Article, Resource

assets = Environment()
dbmongo = MongoEngine()
dbsql = SQLAlchemy()
mail = Mail()
babel = Babel()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'admin.login_view'


def create_app():
    app = Flask(__name__,
                static_url_path='/static',
                static_folder='static',
                instance_relative_config=False)

    # Configurações
    app.config.from_object('webapp.config.default')  # Configuração basica
    app.config.from_envvar('OPAC_CONFIG', silent=True)  # configuração do ambiente

    # Assets
    js = Bundle('js/vendor/jquery-1.11.0.min.js',
                'js/vendor/underscore-min.js',
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

    if app.config['DEBUG']:
        # Toolbar
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension()
        toolbar.init_app(app)
    # Mongo
    dbmongo.init_app(app)
    # SQLAlchemy
    dbsql.init_app(app)
    # Emails
    mail.init_app(app)

    # Interface do admin
    from .models import User, File, Image
    # from .admin import views
    from webapp.admin import views

    admin = flask_admin.Admin(
        app, 'OPAC admin',
        index_view=views.AdminIndexView(),
        template_mode='bootstrap3',
        base_template="admin/opac_base.html")

    admin.add_view(views.CollectionAdminView(Collection, category=lazy_gettext(u'Catálogo'), name=lazy_gettext(u'Coleção')))
    admin.add_view(views.SponsorAdminView(Sponsor, category=lazy_gettext(u'Catálogo'), name=lazy_gettext(u'Financiador')))
    admin.add_view(views.JournalAdminView(Journal, category=lazy_gettext(u'Catálogo'), name=lazy_gettext(u'Periódico')))
    admin.add_view(views.IssueAdminView(Issue, category=lazy_gettext(u'Catálogo'), name=lazy_gettext(u'Fascículo')))
    admin.add_view(views.ArticleAdminView(Article, category=lazy_gettext(u'Catálogo'), name=lazy_gettext(u'Artigo')))
    admin.add_view(views.ResourceAdminView(Resource, category=lazy_gettext(u'Catálogo'), name=lazy_gettext(u'Recursos')))
    admin.add_view(views.FileAdminView(File, dbsql.session, category=lazy_gettext(u'Ativos')))
    admin.add_view(views.ImageAdminView(Image, dbsql.session, category=lazy_gettext(u'Ativos')))
    admin.add_view(views.UserAdminView(User, dbsql.session, category=lazy_gettext(u'Gestão'), name=lazy_gettext(u'Usuário')))

    from .main import main as main_bp
    app.register_blueprint(main_bp)

    app.wsgi_app = ProxyFix(app.wsgi_app)

    return app
