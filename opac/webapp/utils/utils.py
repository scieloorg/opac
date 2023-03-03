# coding: utf-8

import json
import logging
import os
import re
import shutil
from datetime import datetime, timedelta
from uuid import uuid4

import pytz
import requests
import webapp
from citeproc import (
    Citation,
    CitationItem,
    CitationStylesBibliography,
    CitationStylesStyle,
    formatter,
)
from citeproc.source.json import CiteProcJSON
from citeproc_styles import get_style_filepath
from flask import current_app, render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from legendarium.urlegendarium import URLegendarium
from opac_schema.v1.models import AuditLogEntry, Pages
from webapp import models
from webapp.admin.forms import EmailForm
from webapp.utils.page_migration import MigratedPage, PageMigration
from werkzeug.utils import secure_filename

try:
    from PIL import Image
except ImportError:
    Image = None

# caminho para o CSS a ser incluído no HTML do artigo
CSS = "/static/css/style_article_html.css"
REGEX_EMAIL = re.compile(
    r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
    re.IGNORECASE,
)  # RFC 2822 (simplified)
logger = logging.getLogger(__name__)


def namegen_filename(obj, file_data=None):
    """
    Retorna um nome de arquivo seguro para o arquivo subido,
    utilizando o nome (campo "name" do modelo) e mantendo a extensão original
    """

    if isinstance(obj, str):
        _, extension = os.path.splitext(obj)
        return secure_filename("%s%s" % (_, extension))
    else:
        _, extension = os.path.splitext(file_data.filename)
        return secure_filename("%s%s" % (obj.name, extension))


def open_file(file_path, mode="rb", encoding="iso-8859-1"):
    """
    Open file as like object(bytes)
    """
    try:
        return open(file_path, mode=mode, encoding=encoding)
    except IOError:
        raise


def thumbgen_filename(filename):
    """
    Gera o nome do arquivo do thumbnail a partir do  filename.
    """
    name, ext = os.path.splitext(filename)
    return "%s_thumb%s" % (name, ext)


def get_timed_serializer():
    """
    Retorna uma instância do URLSafeTimedSerializer necessário para gerar tokens
    """
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def get_prev_article(articles, article):
    """
    Considerando que a lista de artigos está ordenada pelo atributo ``order``,
    que é um atributo crescente, ou seja, o último artigo é o artigo com maior
    valor no atributo ``order``. A lógica é direta ou seja para retornar o
    artigo anterior subtrai 1 do índice corrente.

    IMPORTANTE: Quando o índice do artigo for igual a 0 devemos retornar None.

    """
    if len(articles) != 0:
        try:
            if articles.index(article) == 0:
                return None
            return articles[articles.index(article) - 1]
        except IndexError:
            return None
    else:
        return None


def get_next_article(articles, article):
    """
    Considerando que a lista de artigos está ordenada pelo atributo ``order``,
    que é um atributo crescente, ou seja, o último artigo é o artigo com maior
    valor no atributo ``order``. A lógica é direta ou seja para retornar o
    próximo artigo soma 1 ao índice corrente.


    IMPORTANTE: Quando o índice do artigo for igual ao tamanho da lista
    devemos retornar None.
    """
    if len(articles) != 0:
        try:
            if len(articles) == articles.index(article):
                return None
            return articles[articles.index(article) + 1]
        except IndexError:
            return None
    else:
        return None


def get_prev_issue(issues, issue):
    """
    A lista de números é ordenada pelos números mais recentes para o mais
    antigos, portanto para retornarmos os números mais antigos, devemos
    caminhar pelo índice do valor menor para o maior, isso justifica
    no preview soma 1 ao índice.

    param: issues é a lista de issue (deve ser ordenado do número mais
    recente para o mais antigo)
    param: issue é o issue corrente.

    IMPORTANTE: A lista de números deve ter mais do que 1 item para que
    possa existir a ideia de anterior e próximo
    """
    try:
        return issues[issues.index(issue) + 1]
    except (ValueError, IndexError):
        return None


def get_next_issue(issues, issue):
    """
    A lista de números é ordenada pelos números mais recentes para o mais
    antigos, portanto para retornarmos os números mais novos, devemos
    caminhar pelo índice do valor maior para o menor, isso justifica
    no preview subtrai 1 ao índice.

    param: issues é a lista de issue (deve ser ordenado do número mais
    recente para o mais antigo)
    param: issue é o issue corrente.

    IMPORTANTE: A lista de números deve ter mais do que 1 item para que
    possa existir a ideia de anterior e próximo
    """
    try:
        index = issues.index(issue) - 1
    except ValueError:
        return None
    if index >= 0:
        return issues[index]
    return None


def get_label_issue(issue):
    label = "Vol. %s " % issue.volume if issue.volume else ""
    label += "No. %s " % issue.number if issue.number else ""
    label += "- %s" % issue.year if issue.year else ""

    return label


def send_email(recipient, subject, html):
    """
    Método auxiliar para envio de emails
    - recipient: destinatario
    - subject: assunto
    - html: corpo da mensagem (formato html)
    Quem envía a mensagem é que for definido na configuração: 'MAIL_DEFAULT_SENDER'

    Retorna:
     - (True, '') em caso de sucesso.
     - (False, 'MENSAGEM DE ERRO/EXCEÇÃO') em caso de exceção/erro
    """
    recipients = [
        recipient,
    ]
    if isinstance(recipient, list):
        recipients = recipient
    try:
        msg = Message(
            subject=subject,
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            recipients=recipients,
            html=html,
        )
        webapp.mail.send(msg)
        return (True, "")
    except Exception as e:
        return (False, e)


def reset_db():
    """
    Apaga todos os dados de todas as tabelas e cria novas tabelas, SEM DADOS!
    """

    webapp.dbsql.drop_all()
    webapp.dbsql.create_all()
    webapp.dbsql.session.commit()


def create_db_tables():
    """
    Cria as tabelas no banco SQL, SEM DADOS!
    """

    try:
        webapp.dbsql.create_all()
        webapp.dbsql.session.commit()
    except Exception as e:
        # TODO: melhorar o informe do erro
        raise e


def create_user(user_email, user_password, user_email_confirmed):
    """
    Cria um novo usuário, com acesso habilitado para acessar no admin.
    O parâmetro: ``user_password`` deve ser a senha em texto plano,
    que sera "hasheada" no momento de salvar o usuário.
    """

    new_user = models.User(
        email=user_email, _password=user_password, email_confirmed=user_email_confirmed
    )
    new_user.define_password(user_password)
    webapp.dbsql.session.add(new_user)
    webapp.dbsql.session.commit()

    return new_user


def generate_thumbnail(input_filename):
    """
    Parâmetro input_filename matriz do thumbnail.

    Caso a geração seja realizado com sucesso deve retorna o path do thumbnail,
    caso contrário None.
    """

    image_root = current_app.config["IMAGE_ROOT"]

    size = (
        current_app.config["THUMBNAIL_HEIGHT"],
        current_app.config["THUMBNAIL_WIDTH"],
    )

    image_path = os.path.join(image_root, thumbgen_filename(input_filename))

    try:
        img = Image.open(input_filename)
        img.thumbnail(size)
        img.save(image_path)
    except KeyError as e:
        logger.error("%s" % e)
    except IOError as e:
        logger.error("%s" % e)
    except Exception as e:
        logger.exception("Unexpected error", e)
    else:
        return image_path


def create_image(image_path, filename, thumbnail=False, check_if_exists=True):
    """
    Função que cria uma imagem para o modelo Image.

    Parâmetro image_path caminho absoluto para a imagem.
    Parâmetro filename no para o arquivo com extensão.
    Parâmetro thumbnail liga/desliga criação de thumbnail.
    Parâmetro check_if_exists verifica se a image existe considera somente o
    nome da imagem.
    """

    image_root = current_app.config["IMAGE_ROOT"]
    if not os.path.isdir(image_root):
        os.makedirs(image_root)
    image_destiation_path = os.path.join(image_root, filename)

    try:
        shutil.copyfile(image_path, image_destiation_path)
    except IOError as e:
        # https://docs.python.org/3/library/exceptions.html#FileNotFoundError
        logger.error("%s" % e)
    else:
        if thumbnail:
            generate_thumbnail(image_destiation_path)

        if check_if_exists:
            img = (
                webapp.dbsql.session.query(models.Image)
                .filter_by(name=filename)
                .first()
            )
            if img:
                return img

        img = models.Image(name=namegen_filename(filename), path="images/" + filename)
        webapp.dbsql.session.add(img)
        webapp.dbsql.session.commit()
        return img


def create_file(file_path, filename, check_if_exists=True):
    """
    Função que cria um arquivo para o modelo File.

    Parâmetro file_path caminho absoluto para o arquivo.
    Parâmetro filename nome do arquivo com extensão.
    Parâmetro check_if_exists verifica se o arquivo existe considera somente o
    nome do arquivo.
    """

    file_root = current_app.config["FILE_ROOT"]
    if not os.path.isdir(file_root):
        os.makedirs(file_root)
    file_destination_path = os.path.join(file_root, filename)

    try:
        shutil.copyfile(file_path, file_destination_path)
    except IOError as e:
        # https://docs.python.org/3/library/exceptions.html#FileNotFoundError
        logger.error("%s" % e)
    else:
        if check_if_exists:
            _file = (
                webapp.dbsql.session.query(models.File).filter_by(name=filename).first()
            )
            if _file:
                return _file

        _file = models.File(name=namegen_filename(filename), path="files/" + filename)
        webapp.dbsql.session.add(_file)
        webapp.dbsql.session.commit()
        return _file


def create_page(name, language, content, journal=None, description=None):
    """
    Função que cria uma página para o modelo Pages.
    Parâmetro name: título da página
    Parâmetro language: idioma do texto da página
    Parâmetro content: conteúdo em HTML da página
    Parâmetro journal: acrônimo do periódico se a página for de periódico
    Parâmetro description: descrição da página
    """
    page = Pages(
        _id=str(uuid4().hex),
        name=name,
        language=language,
        content=content,
        journal=journal,
        description=description,
    )
    page.save()
    return page


def join_html_files_content(revistas_path, acron, files):
    """
    Função que lê os arquivos aboutj.htm, instruct.htm e edboard.htm
    e os junta em um único conteúdo
    Retorna o novo conteúdo
    Parâmetro name: título da página
    Parâmetro language: idioma do texto da página
    Parâmetro content: conteúdo em HTML da página
    Parâmetro journal: acrônimo do periódico se a página for de periódico
    Parâmetro description: descrição da página
    """
    content = []
    unavailable_message = []
    for file in files:
        file_path = os.path.join(revistas_path, acron, file)
        page = webapp.utils.journal_static_page.OldJournalPageFile(file_path)
        if page.unavailable_message:
            unavailable_message.append(
                page.anchor + page.anchor_title + page.unavailable_message
            )
            content.append(unavailable_message[-1])
        else:
            content.append(page.body)
    text = " <!-- UNAVAILABLE MESSAGE: {} --> ".format(len(unavailable_message))
    return "\n".join(content) + text


def migrate_page_create_image(src, dest, check_if_exists=False):
    return create_image(src, dest, check_if_exists).get_absolute_url


def migrate_page_create_file(src, dest, check_if_exists=False):
    return create_file(src, dest, check_if_exists).get_absolute_url


def migrate_page_content(content, language, acron=None, page_name=None):
    """
    Função que migra o conteúdo de qualquer página HTML
    Retorna o novo conteúdo
    Parâmetro content: conteúdo em HTML da página
    Parâmetro acron: acrônimo do periódico se a página for de periódico
    Parâmetro page_name: título da página se não é de periódico
    Parâmetro language: idioma do texto da página
    """
    if content:
        if not acron and not page_name:
            raise IOError("migrate_page_content() requer acron ou page_name")

        pages_source_path = current_app.config["JOURNAL_PAGES_SOURCE_PATH"]
        images_source_path = current_app.config["JOURNAL_IMAGES_SOURCE_PATH"]
        original_website = current_app.config["JOURNAL_PAGES_ORIGINAL_WEBSITE"]

        migration = PageMigration(
            original_website, pages_source_path, images_source_path
        )

        page = MigratedPage(
            migration, content, acron=acron, page_name=page_name, lang=language
        )
        page.migrate_urls(migrate_page_create_file, migrate_page_create_image)
        return page.content


def create_new_journal_page(acron, files, lang):
    """
    Função que cria uma página secundária de um periódico em um idioma e
    é composta pelos arquivos about, editorial board e instrucoes aos autores
    Parâmetro acron: acrônimo do periódico.
    Parâmetro files: about, editorial board e instrucoes aos autores
    Parâmetro lang: idioma da página
    """
    pages_source_path = current_app.config["JOURNAL_PAGES_SOURCE_PATH"]
    content = join_html_files_content(pages_source_path, acron, files)
    if content:
        content = migrate_page_content(content, lang, acron=acron)
        create_page(
            "Página secundária %s (%s)" % (acron.upper(), lang),
            lang,
            content,
            acron,
            "Página secundária do periódico %s" % acron,
        )
        return content


def get_resource_url(resource, type, lang):
    if resource.language == lang and resource.type == type:
        return resource.url
    return None


def get_resources_url(resource_list, type, lang):
    for resource in resource_list:
        resource_url = get_resource_url(resource, type, lang)
        if resource_url:
            return resource_url
    return None


def utc_to_local(utc_dt):
    local_tz = pytz.timezone(current_app.config["LOCAL_ZONE"])

    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)

    return local_tz.normalize(local_dt)


def is_recaptcha_valid(request):
    """
    Verify if the response for the Google recaptcha is valid.
    """
    return (
        requests.post(
            current_app.config["GOOGLE_VERIFY_RECAPTCHA_URL"],
            data={
                "secret": current_app.config["GOOGLE_VERIFY_RECAPTCHA_KEY"],
                "response": request.form["g-recaptcha-response"],
            },
            verify=True,
        )
        .json()
        .get("success", False)
    )


def send_audit_log_daily_report():
    def filter_only_valid_emails(recipients_list):
        validated_emails = []
        for raw_email in recipients_list:
            form = EmailForm(data={"email": raw_email})
            if form.validate():
                validated_emails.append(raw_email)

        return validated_emails

    def collect_recipients_from_conf():
        print(
            "coletamos os emails para envio definidos na conf: AUDIT_LOG_NOTIFICATION_RECIPIENTS"
        )
        recipients_from_conf = current_app.config["AUDIT_LOG_NOTIFICATION_RECIPIENTS"]
        recipients_from_conf_validated = filter_only_valid_emails(recipients_from_conf)
        print(
            "emails definidos na configuração, validados: ",
            recipients_from_conf_validated,
        )
        if len(recipients_from_conf_validated) == 0:
            print("não temos emails (da configuração) válidos, para enviar")
        return recipients_from_conf_validated

    def colect_recipiets_from_users_table():
        active_users = webapp.dbsql.session.query(models.User).filter_by(
            email_confirmed=True
        )
        print("recipients_from_users: ", [u.email for u in active_users])
        return [u.email for u in active_users]

    def prepare_report_email(recipients, records):
        report_date = datetime.today().strftime("%Y-%m-%d")
        collection_acronym = current_app.config["OPAC_COLLECTION"]
        email_subject = (
            "[%s] - Relatório de auditoria de mudanças - últimas 24hs (%s) "
            % (collection_acronym, report_date)
        )
        templ_context = {"records": records, "report_date": report_date}
        email_data = {
            "recipient": recipients,
            "subject": email_subject,
            "html": render_template(
                "admin/email/audit_log_report.html", **templ_context
            ),
        }
        return email_data

    flask_app = webapp.create_app()

    with flask_app.app_context():
        if current_app.config["AUDIT_LOG_NOTIFICATION_ENABLED"]:
            target_datetime = datetime.today() - timedelta(days=1)
            date_range_query = {"created_at": {"$gte": target_datetime}}

            audit_records = AuditLogEntry.objects.filter(
                __raw__=date_range_query
            ).order_by("-created_at")
            audit_records_count = audit_records.count()
            if audit_records_count > 0:
                print("registros encontrados: ", audit_records_count)
                recipients_from_conf_validated = collect_recipients_from_conf()
                recipients_from_users = colect_recipiets_from_users_table()
                all_recipients = recipients_from_conf_validated + recipients_from_users
                print("todos os recipients:", all_recipients)

                for record in audit_records:
                    print(
                        "-> ",
                        record._id,
                        record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    )

                email_data = prepare_report_email(all_recipients, audit_records)
                send_email(**email_data)
            else:
                print("não encontramos registros modificados hoje.")
        else:
            print(
                "O envio de email de auditoria esta desativado. Verifique a conf: AUDIT_LOG_NOTIFICATION_ENABLED"
            )


def asbool(s):
    """Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is a :term:`truthy string`. If ``s`` is already one of the
    boolean values ``True`` or ``False``, return it."""
    truthy = ("t", "true", "y", "yes", "on", "1")

    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy


def fix_journal_last_issue(journal):
    """
    Resolve ausência de preenchimento do atributo `LastIssue.url_segment`
    Teoricamente, o atributo `LastIssue.url_segment` deveria ter sido preenchido
    ao registrar os issues e/ou o journal no website. Mas no fluxo SPF,
    não ocorreu.
    """
    if journal.last_issue is None or journal.last_issue.url_segment:
        return journal.last_issue

    leg_dict = {
        "year_pub": journal.last_issue.year,
        "volume": journal.last_issue.volume,
        "number": journal.last_issue.number,
        "suppl_number": journal.last_issue.suppl_text,
    }
    journal.last_issue.url_segment = URLegendarium(**leg_dict).get_issue_seg()
    return journal.last_issue


def render_citation(csl_json, style="apa", formatter=formatter.html, validate=False):
    """
    Given a csl_json and return a citation

    Link do the csl-json schema: https://github.com/citation-style-language/schema/blob/master/schemas/input/csl-data.json

    Example of csl_json param:
        [
            {
                "id": "wNZLxRjKfGdDw8KGmbNN7qj",
                "DOI": "10.1590/0001-3765202020181115",
                "URL": "http://dx.doi.org/10.1590/0001-3765202020181115",
                "author": [
                    {
                        "family": "SANTOS-SILVA",
                        "given": "JULIANA"
                    },
                    {
                        "family": "ARAÚJO",
                        "given": "TAINAR J."
                    }
                ],
                "container-title": "Scientific Electronic Library Online",
                "container-title-short": "SciELO",
                "issue": "An. Acad. Bras. Ciênc., 2020 92(2)",
                "issued": {
                    "date-parts": [
                        [
                            2020,
                            9
                        ]
                    ]
                },
                "page": "",
                "publisher": "Academia Brasileira de Ciências",
                "title": "Are Fabaceae the principal super-hosts of galls in Brazil?",
                "title-short": "Are Fabaceae the principal super-hosts of galls in Brazil?",
                "type": "research-article",
                "volume": "92"
            }
        ]

    Return a list citation as string.

    """

    bib_source = CiteProcJSON(csl_json)

    style_path = get_style_filepath(style)

    bib_style = CitationStylesStyle(style_path, validate=validate)

    bibliography = CitationStylesBibliography(bib_style, bib_source, formatter)

    # Loop to the citations id on csl_json
    ids = [c.get("id") for c in csl_json]

    for id in ids:
        citation = Citation([CitationItem(id)])
        bibliography.register(citation)

    def warn(citation_item):
        print(
            "WARNING: Reference with key '{}' not found in the bibliography.".format(
                citation_item.key
            )
        )

    bibliography.cite(citation, warn)

    return [str(item) for item in bibliography.bibliography()]
