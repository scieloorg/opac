#!/usr/bin/env python
# coding: utf-8
import os
import sys
import shutil
import fnmatch
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
WEBAPP_PATH = os.path.abspath(os.path.join(HERE, 'webapp'))
sys.path.insert(0, HERE)
sys.path.insert(1, WEBAPP_PATH)

FLASK_COVERAGE = os.environ.get('FLASK_COVERAGE', None)

if FLASK_COVERAGE:
    try:
        import coverage
    except ImportError:
        msg = u'A variável de ambiente %r esta indicando que você quer executar tests com coverage, porém não é possível importar o modulo coverage'
        raise RuntimeError(msg % variable_name)
    COV = None
    if FLASK_COVERAGE:
        COV = coverage.coverage(branch=True, include='opac/webapp/*')
        COV.start()
else:
    COV = None

from webapp import create_app, dbsql, dbmongo, mail
from opac_schema.v1.models import Collection, Sponsor, Journal, Issue, Article
from webapp import utils, controllers
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from webapp.admin.forms import EmailForm
from flask import current_app

app = create_app()
migrate = Migrate(app, dbsql)
manager = Manager(app)
manager.add_command('dbsql', MigrateCommand)


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
@manager.option('-f', '--force', dest='force_delete', default=False)
def reset_dbsql(force_delete=False):
    """
    Remove todos os dados do banco de dados SQL.
    Por padrão: se o banco SQL já existe, o banco não sera modificado.
    Utilize o parametro --force=True para forçar a remoção dos dados.

    Uma vez removidos os dados, todas as tabelas serão criadas vazias.
    """

    db_path = app.config['DATABASE_PATH']
    if not os.path.exists(db_path) or force_delete:
        utils.reset_db()
        print u'O banco esta limpo!'
        print u'Para criar um novo usuário execute o comando: create_superuser'
        print u'python manager.py create_superuser'
    else:
        print u'O banco já existe (em %s).' % db_path
        print u'remova este arquivo manualmente ou utilize --force.'


@manager.command
def create_tables_dbsql(force_delete=False):
    """
    Cria as tabelas necessárias no banco de dados SQL.
    """

    db_path = app.config['DATABASE_PATH']
    if not os.path.exists(db_path):
        utils.create_db_tables()
        print u'As tabelas foram criadas com sucesso!'
    else:
        print u'O banco já existe (em %s).' % db_path
        print u'Para remover e crias as tabelas use o camando:'
        print u'python manager.py reset_dbsql --help'


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
@manager.option('-p', '--pattern', dest='pattern')
def test(pattern='test_*.py'):
    """ Executa tests unitarios.
    Lembre de definir a variável: OPAC_CONFIG="path do arquivo de conf para testing"
    antes de executar este comando:
    > export OPAC_CONFIG="/foo/bar/config.testing" && python manager.py test

    Utilize -p para rodar testes específicos, ex.: test_admin_*.'
    """

    if COV and not FLASK_COVERAGE:
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    tests = unittest.TestLoader().discover('tests', pattern=pattern)
    result = unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        # basedir = os.path.abspath(os.path.dirname(__file__))
        # covdir = 'tmp/coverage'
        # COV.html_report(directory=covdir)
        # print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

    if result.wasSuccessful():
        return sys.exit()
    else:
        return sys.exit(1)


@manager.command
@manager.option('-d', '--directory', dest="pattern")
def upload_images(directory='.'):
    """
    Esse comando realiza um cadastro em massa de images com extensões:
    ('*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp') de um diretório determinado
    pelo parâmetro --directory (utilizar caminho absoluto).

    Cada imagem cadastrada receberá um nome que será o slug do nome do arquivo,
    ex.:

    Nome do arquivo no sistema de arquivo: logo-scielo-journal-brasil.png
    Nome do arquivo após o cadastro na entidade Image: logo_scielo_journal_brasilpng
    """

    extensions = ('*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp')

    print "Coletando todas a imagens da pasta: %s" % directory

    for root, dirnames, filenames in os.walk(directory):
        for extension in extensions:
            for filename in fnmatch.filter(filenames, extension):

                image_path = os.path.join(root, filename)

                print "Imagem: %s" % image_path

                dst_path = os.path.join(app.config['MEDIA_ROOT'], filename)

                shutil.copyfile(image_path, dst_path)

                tumb_path = utils.generate_thumbnail(image_path,
                                                     app.config['MEDIA_ROOT'])

                print "Thumbnail: %s" % tumb_path

                img = Image(name=utils.slugify(filename), path=filename)

                dbsql.session.add(img)
                dbsql.session.commit()

if __name__ == '__main__':
    manager.run()
