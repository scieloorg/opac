# coding: utf-8

import logging
from raven.contrib.flask import Sentry

from flask import Flask
from flask_htmlmin import HTMLMIN
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import flask_admin
from flask_mail import Mail
from flask_babelex import Babel
from flask_babelex import lazy_gettext
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.routing import BaseConverter

from opac_schema.v1.models import (
    Collection,
    Sponsor,
    Journal,
    Issue,
    Article,
    News,
    Pages,
    PressRelease)

login_manager = LoginManager()
dbmongo = MongoEngine()
dbsql = SQLAlchemy()
mail = Mail()
babel = Babel()
sentry = Sentry()

from .main import custom_filters  # noqa


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def create_app():
    app = Flask(__name__,
                static_url_path='/static',
                static_folder='static',
                instance_relative_config=False)

    app.url_map.converters['regex'] = RegexConverter

    # Configurações
    app.config.from_object('webapp.config.default')  # Configuração basica
    app.config.from_envvar('OPAC_CONFIG', silent=True)  # configuração do ambiente

    # Sentry:
    if app.config['USE_SENTRY']:
        dsn = app.config['SENTRY_DSN']
        sentry.init_app(app, dsn=dsn, logging=True, level=logging.ERROR)

    # login
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'admin.login_view'
    login_manager.init_app(app)

    # Minificando o HTML
    if not app.config['DEBUG']:
        HTMLMIN(app)

    # Registrando os filtros
    app.jinja_env.filters['trans_alpha2'] = custom_filters.trans_alpha2
    app.jinja_env.filters['datetimefilter'] = custom_filters.datetimefilter

    # i18n
    babel.init_app(app)
    # Debug Toolbar
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

    admin.add_view(views.CollectionAdminView(Collection, category=lazy_gettext('Catálogo'), name=lazy_gettext('Coleção')))
    admin.add_view(views.JournalAdminView(Journal, category=lazy_gettext('Catálogo'), name=lazy_gettext('Periódico')))
    admin.add_view(views.IssueAdminView(Issue, category=lazy_gettext('Catálogo'), name=lazy_gettext('Número')))
    admin.add_view(views.ArticleAdminView(Article, category=lazy_gettext('Catálogo'), name=lazy_gettext('Artigo')))
    admin.add_view(views.SponsorAdminView(Sponsor, category=lazy_gettext('Catálogo'), name=lazy_gettext('Financiador')))
    admin.add_view(views.PressReleaseAdminView(PressRelease, category=lazy_gettext('Catálogo'), name=lazy_gettext('Press Release')))
    admin.add_view(views.NewsAdminView(News, name=lazy_gettext('Notícias')))
    admin.add_view(views.FileAdminView(File, dbsql.session, category=lazy_gettext('Ativos')))
    admin.add_view(views.ImageAdminView(Image, dbsql.session, category=lazy_gettext('Ativos')))
    admin.add_view(views.PagesAdminView(Pages, name=lazy_gettext('Páginas')))
    admin.add_view(views.UserAdminView(User, dbsql.session, category=lazy_gettext('Gestão'), name=lazy_gettext('Usuário')))

    from .main import main as main_bp
    app.register_blueprint(main_bp)

    app.wsgi_app = ProxyFix(app.wsgi_app)

    return app
