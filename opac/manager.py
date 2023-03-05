#!/usr/bin/env python
# coding: utf-8
import fnmatch
import json
import os
import sys
import unittest
from uuid import uuid4

HERE = os.path.dirname(os.path.abspath(__file__))
WEBAPP_PATH = os.path.abspath(os.path.join(HERE, "webapp"))
sys.path.insert(0, HERE)
sys.path.insert(1, WEBAPP_PATH)

FLASK_COVERAGE = os.environ.get("FLASK_COVERAGE", None)

if FLASK_COVERAGE:
    try:
        import coverage
    except ImportError:
        msg = "Não é possível importar o modulo coverage"
        raise RuntimeError(msg)
    COV = None
    if FLASK_COVERAGE:
        COV = coverage.coverage(branch=True, include="opac/webapp/*")
        COV.start()
else:
    COV = None

from flask_migrate import Migrate, MigrateCommand  # noqa
from flask_script import Manager, Shell  # noqa
from opac_schema.v1.models import (  # noqa
    Article,
    AuditLogEntry,
    Collection,
    Issue,
    Journal,
    Sponsor,
)
from webapp import controllers  # noqa
from webapp import cache, create_app, dbmongo, dbsql, mail  # noqa
from webapp.admin.forms import EmailForm  # noqa
from webapp.tasks import clear_scheduler, setup_scheduler  # noqa
from webapp.utils import (  # noqa
    create_db_tables,
    create_new_journal_page,
    create_user,
    reset_db,
    send_audit_log_daily_report,
)
from webapp.utils.journal_static_page import PAGE_NAMES_BY_LANG  # noqa

app = create_app()
migrate = Migrate(app, dbsql)
manager = Manager(app)
manager.add_command("dbsql", MigrateCommand)


def make_shell_context():
    app_models = {
        "Collection": Collection,
        "Sponsor": Sponsor,
        "Journal": Journal,
        "Issue": Issue,
        "Article": Article,
        "AuditLogEntry": AuditLogEntry,
    }
    return dict(
        app=app, dbsql=dbsql, dbmongo=dbmongo, mail=mail, cache=cache, **app_models
    )


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
@manager.option("-f", "--force", dest="force_clear", default=False)
def invalidate_cache(force_clear=False):
    def clear_cache():
        keys_invalidated = cache.clear()
        print("Chaves invalidadas: %s" % keys_invalidated)
        print("Cache zerado com sucesso!")

    if force_clear:
        clear_cache()
    else:
        # pedimos confirmação
        user_confirmation = None
        while user_confirmation is None:
            user_confirmation = input(
                "Tem certeza que deseja limpar todo o cache? [y/N]: "
            ).strip()
            if user_confirmation.lower() == "y":
                clear_cache()
            elif user_confirmation.lower() == "n":
                print("O cache permance sem mudanças!")
            else:
                user_confirmation = None
                print('Resposta inválida. Responda "y" ou "n" (sem aspas)')


@manager.command
@manager.option("-p", "--pattern", dest="pattern")
@manager.option("-f", "--force", dest="force_clear", default=False)
def invalidate_cache_pattern(pattern, force_clear=False):
    _redis_cli = cache.cache._client

    def count_key_pattern(pattern):
        keys_found = _redis_cli.scan_iter(match=pattern)
        return len([k for k in keys_found])

    def delete_cache_pattern(pattern):
        print("Removendo do cache as chaves com pattern: %s" % pattern)
        keys_found = _redis_cli.scan_iter(match=pattern)
        deleted_keys_count = _redis_cli.delete(*keys_found)
        print("%s chaves removidas do cache" % deleted_keys_count)

    if not pattern:
        print("Não é possível buscar chaves se o pattern é vazio!")
        print("O cache permance sem mudanças!")
    else:
        if force_clear:
            keys_found_count = count_key_pattern(pattern)
            if keys_found_count > 0:
                delete_cache_pattern(pattern)
            else:
                print("Não foi encontrada nenhuma chave pelo pattern: %s" % pattern)
        else:
            # pedimos confirmação
            user_confirmation = None
            while user_confirmation is None:
                user_confirmation = input(
                    "Tem certeza que deseja limpar o cache filtrando pelo pattern: %s? [y/N]: "
                    % pattern
                ).strip()
                if user_confirmation.lower() == "y":
                    keys_found_count = count_key_pattern(pattern)
                    if keys_found_count > 0:
                        delete_cache_pattern(pattern)
                    else:
                        print(
                            "Não foi encontrada nenhuma chave pelo pattern: %s"
                            % pattern
                        )
                elif user_confirmation.lower() == "n":
                    print("O cache permance sem mudanças!")
                else:
                    user_confirmation = None
                    print('Resposta inválida. Responda "y" ou "n" (sem aspas)')


@manager.command
@manager.option("-f", "--force", dest="force_delete", default=False)
def reset_dbsql(force_delete=False):
    """
    Remove todos os dados do banco de dados SQL.
    Por padrão: se o banco SQL já existe, o banco não sera modificado.
    Utilize o parametro --force=True para forçar a remoção dos dados.

    Uma vez removidos os dados, todas as tabelas serão criadas vazias.
    """

    db_path = app.config["DATABASE_PATH"]
    if not os.path.exists(db_path) or force_delete:
        reset_db()
        print("O banco esta limpo!")
        print("Para criar um novo usuário execute o comando: create_superuser")
        print("python manager.py create_superuser")
    else:
        print("O banco já existe (em %s)." % db_path)
        print("remova este arquivo manualmente ou utilize --force.")


@manager.command
def create_tables_dbsql(force_delete=False):
    """
    Cria as tabelas necessárias no banco de dados SQL.
    """

    db_path = app.config["DATABASE_PATH"]
    if not os.path.exists(db_path):
        create_db_tables()
        print("As tabelas foram criadas com sucesso!")
    else:
        print("O banco já existe (em %s)." % db_path)
        print("Para remover e crias as tabelas use o camando:")
        print("python manager.py reset_dbsql --help")


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
        user_email = input("Email: ").strip()
        if user_email == "":
            user_email = None
            print("Email não pode ser vazio")
        else:
            form = EmailForm(data={"email": user_email})
            if not form.validate():
                user_email = None
                print("Deve inserir um email válido!")
            elif controllers.get_user_by_email(user_email):
                user_email = None
                print("Já existe outro usuário com esse email!")

    os.system("stty -echo")
    while user_password is None:
        user_password = input("Senha: ").strip()
        if user_password == "":
            user_password = None
            print("Senha não pode ser vazio")
    os.system("stty echo")

    email_confirmed = input("\nEmail confirmado? [y/N]: ").strip()
    if email_confirmed.upper() in ("Y", "YES"):
        email_confirmed = True
    else:
        email_confirmed = False
        print("Deve enviar o email de confirmação pelo admin")

    # cria usuario
    create_user(user_email, user_password, email_confirmed)
    print("Novo usuário criado com sucesso!")


@manager.command
@manager.option("-p", "--pattern", dest="pattern")
@manager.option("-f", "--failfast", dest="failfast")
def test(pattern=None, failfast=False):
    """Executa tests unitarios.
    Lembre de definir a variável: OPAC_CONFIG="path do arquivo de conf para testing"
    antes de executar este comando:
    > export OPAC_CONFIG="/foo/bar/config.testing" && python manager.py test

    Utilize -p para rodar testes específicos'

    ex.: export OPAC_CONFIG="config/templates/testing.template" && python opac/manager.py test -p "test_main_views"
    """
    failfast = True if failfast else False

    if COV and not FLASK_COVERAGE:
        os.environ["FLASK_COVERAGE"] = "1"
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    if pattern is None:
        tests = unittest.TestLoader().discover("tests")
    else:
        tests = unittest.TestLoader().loadTestsFromName("tests." + pattern)

    result = unittest.TextTestRunner(verbosity=2, failfast=failfast).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print("Coverage Summary:")
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
@manager.option("-d", "--directory", dest="pattern")
def upload_images(directory="."):
    """
    Esse comando realiza um cadastro em massa de images com extensões contidas
    na variável: app.config['IMAGES_ALLOWED_EXTENSIONS_RE'] de um diretório
    determinado pelo parâmetro --directory (utilizar caminho absoluto).
    """

    extensions = app.config["IMAGES_ALLOWED_EXTENSIONS_RE"]

    print("Coletando todas a imagens da pasta: %s" % directory)

    for root, dirnames, filenames in os.walk(directory):
        for extension in extensions:
            for filename in fnmatch.filter(filenames, extension):
                image_path = os.path.join(root, filename)

                create_image(image_path, filename)


@manager.command
@manager.option("-d", "--domain", dest="domain")
@manager.option("-f", "--filename", dest="filename")
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
        collection.name = data["collection"]["name"]
        collection.address1 = data["collection"]["address1"]
        collection.address2 = data["collection"]["address2"]

        print("Cadastrando as imagens da coleção %s" % collection.name)

        for imgs in data["collection"]["images"]:
            for key, val in imgs.items():
                img = create_image(val, os.path.basename(val))

                setattr(collection, key, "%s%s" % (domain, img.get_absolute_url))

        print("Cadastrando os financiadores da coleção %s" % collection.name)

        sponsors = []

        for _ in data["sponsors"]:
            sponsor = Sponsor()
            sponsor._id = str(uuid4().hex)
            sponsor.order = _["order"]
            sponsor.name = _["name"]
            img = create_image(_["logo_path"], os.path.basename(_["logo_path"]))
            sponsor.logo_url = "%s%s" % (domain, img.get_absolute_url)
            sponsor.url = _["url"]
            sponsor.save()
            sponsors.append(sponsor)

        collection.sponsors = sponsors

        collection.save()

    else:
        print("Nenhuma coleção encontrada!")


@manager.command
@manager.option("-f", "--filename", dest="filename")
def populate_pdfs_path_html_version(
    filename="fixtures/pdfs_path_file_html_version.json",
):
    """
    Esse comando tem como responsabilidade enriquecer os registros de artigos com o caminho da URL do site anterior para os PDFs.

    Além do nome dos arquivos em PDF o site precisa dos caminhos dos PDFs para que seja possível resolver URLs como http://www.scielo.br/pdf/aa/v36n2/v36n2a09.pdf

    O arquivo ``fixtures/pdfs_path_file_html_version.json` é extraído uma única vez, contendo todos os PIDs da versão HTML, caminho dos PDFs e idioma.

    Estrutura do arquivo: ``pdfs_path_file_html_version.json``:

    [
      {
        "pid": "S0044-59672004000100001",
        "file_path": "/pdf/aa/v34n1/v34n1a01.pdf",
        "lang": "pt"
      },
    ]

    """

    with open(filename) as fp:
        data_json = json.load(fp)

    for art_pdf_path in data_json:
        art = controllers.get_article_by_pid(art_pdf_path["pid"])

        if art.pdfs:
            for pdf in art.pdfs:
                if art_pdf_path.get("lang", "") == pdf.get("lang"):
                    pdf["file_path"] = art_pdf_path.get("file_path")

            art.save()

            print(
                "PDF do PID: %s atualizado com sucesso, caminho %s"
                % (art_pdf_path.get("pid"), art_pdf_path.get("file_path"))
            )
        else:
            print(
                "PDF do PID: %s não encontrado na base de dados do OPAC."
                % (art_pdf_path.get("pid"))
            )


@manager.command
def populate_journal_pages():
    """
    Esse comando faz o primeiro registro das páginas secundárias
    dos periódicos localizado em /data/pages.
    Cada vez que executa cria um novo registro.

    As páginas dos periódico SciELO contém a seguinte estrutura:

    - eaboutj.htm
    - einstruc.htm
    - eedboard.htm
    - esubscrp.htm (Assinatura)

    Sendo que o prefixo "e" indica Espanhol, prefixo "i" Inglês e o prefixo "p"
    português.

    OBS.: A extensão dos html é htm.

    Assinatura não esta sendo importada conforme mencionado no tk:
    https://github.com/scieloorg/opac/issues/630
    """
    acron_list = [journal.acronym for journal in Journal.objects.all()]
    j_total = len(acron_list)
    done = 0
    for j, acron in enumerate(sorted(acron_list)):
        print("{}/{} {}".format(j + 1, j_total, acron))
        for lang, files in PAGE_NAMES_BY_LANG.items():
            create_new_journal_page(acron, files, lang)
            done += 1
    print("Páginas: {}\nPeriódicos: {}".format(done, j_total))


@manager.command
@manager.option("-c", "--cronstr", dest="cron_string")
def setup_scheduler_tasks(cron_string=None):
    cron_string = cron_string or app.config["MAILING_CRON_STRING"]
    if not cron_string:
        print(
            "Valor de cron nulo para o scheduler. Definit cron pelo parâmetro ou pela var env."
        )
        return sys.exit(1)
    queue_name = "mailing"
    clear_scheduler(queue_name)
    setup_scheduler(send_audit_log_daily_report, queue_name, cron_string)


@manager.command
def clear_scheduler_tasks():
    clear_scheduler(queue_name="mailing")


@manager.command
def send_audit_log_emails():
    print("coletando registros de auditoria modificados hoje!")
    print(
        "envio de notificações habilitado? (AUDIT_LOG_NOTIFICATION_ENABLED): ",
        app.config["AUDIT_LOG_NOTIFICATION_ENABLED"],
    )
    print(
        "lista recipients (além dos usuários) AUDIT_LOG_NOTIFICATION_RECIPIENTS: ",
        app.config["AUDIT_LOG_NOTIFICATION_RECIPIENTS"],
    )
    send_audit_log_daily_report()


if __name__ == "__main__":
    manager.run()
