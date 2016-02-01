#!/usr/bin/env python
# coding: utf-8
import sys
import os
import unittest
import coverage
from app import create_app, dbsql, dbmongo, mail
from opac_schema.v1.models import Collection, Sponsor, Journal, Issue, Article
from app import utils, controllers
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from app.admin.forms import EmailForm
from flask import current_app

COV = None
app = create_app(os.getenv('OPAC_CONFIG'))
migrate = Migrate(app, dbsql)
manager = Manager(app)
manager.add_command('dbsql', MigrateCommand)

if os.environ.get('FLASK_COVERAGE'):
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


def make_shell_context():
    app_models = {
        'Collection': Collection,
        'Sponsor': Sponsor,
        'Journal': Journal,
        'Issue': Issue,
        'Article': Article,
    }
    return dict(app=app, dbsql=dbsql, dbmongo=dbmongo, mail=mail, **app_models)
manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
@manager.option('-f', '--force', dest='force_delete', default=False,
                help=u'Forçar a remoção dos dados')
def reset_dbsql(force_delete=False):
    """
    Remove todos os dados do banco de dados SQL.
    Por padrão, se o banco SQL já existe, o banco não é modificado.
    Utilize o parametro --force=True para forçar a remoção dos dados.

    Uma vez removidos os dados, todas as tabelas serão criadas.
    """

    db_path = app.config['DATABASE_PATH']
    if not os.path.exists(db_path) or force_delete:
        utils.reset_db()
        print 'O banco esta limpo!'
        print 'Para criar um novo usuário execute o comando: create_superuser'
        print 'python manager.py create_superuser --help'
    else:
        print 'O banco já existe (em %s).' % db_path
        print 'remova este arquivo manualmente ou utilize --force.'


@manager.command
def create_superuser():
    """
    Cria um novo usuário a partir dos dados inseridos na linha de comandos.
    Para criar um novo usuário é necessario preencher:
    - email (deve ser válido é único, se já existe outro usuário com esse email deve inserir outro);
    - senha (modo echo off)
    - e se o usuário tem email confirmado (caso sim, pode fazer logim, caso que não, deve verificar por email)
    """
    user_email = None
    user_password = None

    while user_email is None:
        user_email = raw_input(u'Email: ').strip()
        if user_email == '':
            user_email = None
            print u'Email não pode ser vazio'
        else:
            form = EmailForm(data={'email': user_email})
            if not form.validate():
                user_email = None
                print u'Deve inserir um email válido!'
            elif controllers.get_user_by_email(user_email):
                user_email = None
                print u'Já existe outro usuário com esse email!'

    os.system("stty -echo")
    while user_password is None:
        user_password = raw_input(u'Senha: ').strip()
        if user_password == '':
            user_password = None
            print u'Senha não pode ser vazio'
    os.system("stty echo")

    email_confirmed = raw_input('\nEmail confirmado? [y/N]: ').strip()
    if email_confirmed.upper() in ('Y', 'YES'):
        email_confirmed = True
    else:
        email_confirmed = False
        print u'Deve enviar o email de confirmação pelo admin'

    # cria usuario
    utils.create_user(user_email, user_password, email_confirmed)
    print u'Novo usuário criado com sucesso!'


@manager.command
@manager.option('-v', '--verbosity', dest='verbosity', default=2)
def test(coverage=False, verbosity=2):
    """ Executa tests unitarios.
    Lembre de definir a variável: OPAC_CONFIG="config.testing" antes de executar este comando:
    > export OPAC_CONFIG="config.testing" && python manager.py test
    """
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=verbosity).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.erase()

    if result.wasSuccessful():
        return sys.exit()
    else:
        return sys.exit(1)

if __name__ == '__main__':
    manager.run()
