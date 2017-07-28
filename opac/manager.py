#!/usr/bin/env python
# coding: utf-8
import os
import sys
import json
import fnmatch
import unittest
from uuid import uuid4

HERE = os.path.dirname(os.path.abspath(__file__))
WEBAPP_PATH = os.path.abspath(os.path.join(HERE, 'webapp'))
sys.path.insert(0, HERE)
sys.path.insert(1, WEBAPP_PATH)

FLASK_COVERAGE = os.environ.get('FLASK_COVERAGE', None)

if FLASK_COVERAGE:
    try:
        import coverage
    except ImportError:
        msg = 'Não é possível importar o modulo coverage'
        raise RuntimeError(msg)
    COV = None
    if FLASK_COVERAGE:
        COV = coverage.coverage(branch=True, include='opac/webapp/*')
        COV.start()
else:
    COV = None

from webapp import create_app, dbsql, dbmongo, mail  # noqa
from opac_schema.v1.models import Collection, Sponsor, Journal, Issue, Article  # noqa
from webapp import controllers  # noqa
from webapp.utils import reset_db, create_db_tables, create_user, create_image, create_page, extract_images, open_file  # noqa
from flask_script import Manager, Shell  # noqa
from flask_migrate import Migrate, MigrateCommand  # noqa
from webapp.admin.forms import EmailForm  # noqa

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
        reset_db()
        print('O banco esta limpo!')
        print('Para criar um novo usuário execute o comando: create_superuser')
        print('python manager.py create_superuser')
    else:
        print('O banco já existe (em %s).' % db_path)
        print('remova este arquivo manualmente ou utilize --force.')


@manager.command
def create_tables_dbsql(force_delete=False):
    """
    Cria as tabelas necessárias no banco de dados SQL.
    """

    db_path = app.config['DATABASE_PATH']
    if not os.path.exists(db_path):
        create_db_tables()
        print('As tabelas foram criadas com sucesso!')
    else:
        print('O banco já existe (em %s).' % db_path)
        print('Para remover e crias as tabelas use o camando:')
        print('python manager.py reset_dbsql --help')


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
        user_email = input('Email: ').strip()
        if user_email == '':
            user_email = None
            print('Email não pode ser vazio')
        else:
            form = EmailForm(data={'email': user_email})
            if not form.validate():
                user_email = None
                print('Deve inserir um email válido!')
            elif controllers.get_user_by_email(user_email):
                user_email = None
                print('Já existe outro usuário com esse email!')

    os.system("stty -echo")
    while user_password is None:
        user_password = input('Senha: ').strip()
        if user_password == '':
            user_password = None
            print('Senha não pode ser vazio')
    os.system("stty echo")

    email_confirmed = input('\nEmail confirmado? [y/N]: ').strip()
    if email_confirmed.upper() in ('Y', 'YES'):
        email_confirmed = True
    else:
        email_confirmed = False
        print('Deve enviar o email de confirmação pelo admin')

    # cria usuario
    create_user(user_email, user_password, email_confirmed)
    print('Novo usuário criado com sucesso!')


@manager.command
@manager.option('-p', '--pattern', dest='pattern')
@manager.option('-f', '--failfast', dest='failfast')
def test(pattern='test_*.py', failfast=False):
    """ Executa tests unitarios.
    Lembre de definir a variável: OPAC_CONFIG="path do arquivo de conf para testing"
    antes de executar este comando:
    > export OPAC_CONFIG="/foo/bar/config.testing" && python manager.py test

    Utilize -p para rodar testes específicos, ex.: test_admin_*.'
    """
    failfast = True if failfast else False

    if COV and not FLASK_COVERAGE:
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    tests = unittest.TestLoader().discover('tests', pattern=pattern)

    result = unittest.TextTestRunner(verbosity=2, failfast=failfast).run(tests)

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
    Esse comando realiza um cadastro em massa de images com extensões contidas
    na variável: app.config['IMAGES_ALLOWED_EXTENSIONS_RE'] de um diretório
    determinado pelo parâmetro --directory (utilizar caminho absoluto).
    """

    extensions = app.config['IMAGES_ALLOWED_EXTENSIONS_RE']

    print("Coletando todas a imagens da pasta: %s" % directory)

    for root, dirnames, filenames in os.walk(directory):
        for extension in extensions:
            for filename in fnmatch.filter(filenames, extension):

                image_path = os.path.join(root, filename)

                create_image(image_path, filename)


@manager.command
@manager.option('-d', '--domain', dest="domain")
@manager.option('-f', '--filename', dest="filename")
def populate_database(domain="http://127.0.0.1", filename="fixtures/default_info.json"):
    """
    Esse comando realiza o cadastro dos metadados de uma coleção a partir de um
    arquivo JSON, localizado em: fixtures/default_info.json.

    Por padrão o conteúdo é o da coleção SciELO Brasil.

    As imagens são coletadas da pasta: fixtures/imgs
    """

    data = json.load(open(filename))

    collection = Collection.objects.first()

    if collection:
        collection.name = data['collection']['name']
        collection.address1 = data['collection']['address1']
        collection.address2 = data['collection']['address2']

        print("Cadastrando as imagens da coleção %s" % collection.name)

        for imgs in data['collection']['images']:

            for key, val in imgs.items():

                img = create_image(val, os.path.basename(val))

                setattr(collection, key, '%s%s' % (domain, img.get_absolute_url))

        print("Cadastrando os financiadores da coleção %s" % collection.name)

        sponsors = []

        for _ in data['sponsors']:
            sponsor = Sponsor()
            sponsor._id = str(uuid4().hex)
            sponsor.name = _['name']
            img = create_image(_['logo_path'], os.path.basename(_['logo_path']))
            sponsor.logo_url = '%s%s' % (domain, img.get_absolute_url)
            sponsor.url = _['url']
            sponsor.save()
            sponsors.append(sponsor)

        collection.sponsors = sponsors

        collection.save()

    else:
        print("Nenhuma coleção encontrada!")


@manager.command
def populate_journal_pages(directory=app.config['PAGE_PATH']):
    """
    Esse comando cadastra as páginas secundárias dos periódicos localizado em
    data/pages.

    As páginas dos periódico SciELO contém a seguinte estrutura:

    - eaboutj.htm
    - einstruc.htm
    - eedboard.htm
    - esubscrp.htm (Assinatura)

    Sendo que o prefixo "e" indica Espanhol, prefixo "i" Inglês e o prefixo "p"
    português.

    OBS.: A extensão dos html é htm.

    Assinatura não esta sendo importada conforme mencionado no tk: https://github.com/scieloorg/opac/issues/630


    """
    acron_list = [journal.acronym for journal in Journal.objects.all()]

    file_names = {'en': ['iaboutj.htm',
                         'iedboard.htm',
                         'iinstruc.htm'],
                  'pt_BR': ['paboutj.htm',
                            'pedboard.htm',
                            'pinstruc.htm'],
                  'es': ['eaboutj.htm',
                         'eedboard.htm',
                         'einstruc.htm'],
                  }

    for acron in acron_list:
        journal_dir = os.path.join(directory, acron)

        for lang, files in file_names.items():
            content = ''
            print("Cadastrando as páginas do periódico com acrônimo: %s idioma: %s" % (acron, lang))

            for file in files:
                file_path = os.path.join(journal_dir, file)

                try:
                    fp = open_file(file_path, 'r', encoding='iso-8859-1')
                except IOError as e:
                    print(e)
                else:
                    content += fp.read()

                images_list = extract_images(content)

                for image in images_list:
                    image_name = '%s_%s' % (acron, os.path.basename(image))
                    image_path = os.path.join(journal_dir, os.path.basename(image))

                    try:
                        # Verifica se a imagem existe
                        open_file(image_path, mode='r')
                    except IOError as e:
                        print(e)
                    else:
                        img = create_image(image_path, image_name, thumbnail=True)
                        content = content.replace(image, img.get_absolute_url)

            if content:
                create_page('Página secundária %s (%s)' % (acron.upper(), lang),
                            lang, content, acron, 'Página secundária do periódico %s' % acron)


if __name__ == '__main__':
    manager.run()
