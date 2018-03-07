# coding: utf-8

import os
import re
import pytz
import shutil
import logging
from uuid import uuid4
from datetime import datetime, timedelta

from werkzeug import secure_filename
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import current_app, render_template
import webapp
import requests
from .journal_static_page import JournalStaticPage
from webapp import models
from webapp.admin.forms import EmailForm

from opac_schema.v1.models import Pages, AuditLogEntry

try:
    from PIL import Image
except ImportError:
    Image = None

CSS = "/static/css/style_article_html.css"  # caminho para o CSS a ser incluído no HTML do artigo
REGEX_EMAIL = re.compile(
    r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
    re.IGNORECASE)  # RFC 2822 (simplified)
logger = logging.getLogger(__name__)


def namegen_filename(obj, file_data=None):
    """
        Retorna um nome de arquivo seguro para o arquivo subido,
        utilizando o nome (campo "name" do modelo) e mantendo a extensão original
    """

    if isinstance(obj, str):
        _, extension = os.path.splitext(obj)
        return secure_filename('%s%s' % (_, extension))
    else:
        _, extension = os.path.splitext(file_data.filename)
        return secure_filename('%s%s' % (obj.name, extension))


def open_file(file_path, mode='rb', encoding='iso-8859-1'):
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
    return '%s_thumb%s' % (name, ext)


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
    if len(issues) >= 2:
        try:
            return issues[issues.index(issue) + 1]
        except IndexError:
            return None
    else:
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

    if len(issues) >= 2:
        try:
            # Caso o número seja o primeiro retorna None
            if issues.index(issue) == 0:
                return None
            return issues[issues.index(issue) - 1]
        except IndexError:
            return None
    else:
        return None


def get_label_issue(issue):
    label = 'Vol. %s ' % issue.volume if issue.volume else ''
    label += 'No. %s ' % issue.number if issue.number else ''
    label += '- %s' % issue.year if issue.year else ''

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
    recipients = [recipient, ]
    if isinstance(recipient, list):
        recipients = recipient
    try:
        msg = Message(subject=subject,
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=recipients,
                      html=html)
        webapp.mail.send(msg)
        return (True, '')
    except Exception as e:
        return (False, e.message)


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
        email=user_email,
        _password=user_password,
        email_confirmed=user_email_confirmed)
    new_user.define_password(user_password)
    webapp.dbsql.session.add(new_user)
    webapp.dbsql.session.commit()

    return new_user


def generate_thumbnail(input_filename):
    """
    Parâmento input_filename matriz do thumbnail.

    Caso a geração seja realizado com sucesso deve retorna o path do thumbnail,
    caso contrário None.
    """

    image_root = current_app.config['IMAGE_ROOT']

    size = (current_app.config["THUMBNAIL_HEIGHT"],
            current_app.config["THUMBNAIL_WIDTH"])

    image_path = os.path.join(image_root, thumbgen_filename(input_filename))

    try:
        img = Image.open(input_filename)
        img.thumbnail(size)
        img.save(image_path)
    except KeyError as e:
        logger.error(u'%s' % e)
    except IOError as e:
        logger.error(u'%s' % e)
    except Exception as e:
        logger.exception('Unexpected error', e)
    else:
        return image_path


def create_image(image_path, filename, thumbnail=False, check_if_exists=True):
    """
    Função que cria uma imagem para o modelo Image.

    Parâmento image_path caminho absoluto para a imagem.
    Parâmento filename no para o arquivo com extensão.
    Parâmento thumbnail liga/desliga criação de thumbnail.
    Parâmento check_if_exists verifica se a image existe considera somente o
    nome da imagem.
    """

    image_root = current_app.config['IMAGE_ROOT']
    if not os.path.isdir(image_root):
        os.makedirs(image_root)
    image_destiation_path = os.path.join(image_root, filename)

    try:
        shutil.copyfile(image_path, image_destiation_path)
    except IOError as e:
        # https://docs.python.org/3/library/exceptions.html#FileNotFoundError
        logger.error(u'%s' % e)
    else:
        if thumbnail:
            generate_thumbnail(image_destiation_path)

        if check_if_exists:
            img = webapp.dbsql.session.query(
                models.Image).filter_by(name=filename).first()
            if img:
                return img

        img = models.Image(name=namegen_filename(filename),
                           path='images/' + filename)
        webapp.dbsql.session.add(img)
        webapp.dbsql.session.commit()
        return img


def create_page(name, language, content, journal=None, description=None):

    page = Pages(_id=str(uuid4().hex), name=name, language=language,
                 content=content, journal=journal, description=description)

    page.save()

    return page


def fix_page_content(filename, content):
    """
    Extract the header and the footer of the page
    Insert the anchor based on filename
    """
    return JournalStaticPage(filename, content).body


def extract_images(content):
    """
    Return a list of images to be collect from content
    Try get imgs by href e src tags.
    """

    return re.findall('src="([^"]+)"', content)


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


def do_request(url, params):
    try:
        response = requests.get(url, params=params)
    except:
        return None
    if response.status_code == 200:
        return response.content
    return None


def do_request_json(url, params):
    try:
        response = requests.get(url, params=params)
    except:
        return {}
    if response.status_code == 200:
        return response.json()
    return {}


def utc_to_local(utc_dt):
    local_tz = pytz.timezone(current_app.config['LOCAL_ZONE'])

    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)

    return local_tz.normalize(local_dt)


def is_recaptcha_valid(request):
    """
    Verify if the response for the Google recaptcha is valid.
    """
    return requests.post(
        current_app.config["GOOGLE_VERIFY_RECAPTCHA_URL"],
        data={
            'secret': current_app.config["GOOGLE_VERIFY_RECAPTCHA_KEY"],
            'response': request.form['g-recaptcha-response'],
        },
        verify=True
    ).json().get("success", False)


def send_audit_log_daily_report():

    def filter_only_valid_emails(recipients_list):
        validated_emails = []
        for raw_email in recipients_list:
            form = EmailForm(data={'email': raw_email})
            if form.validate():
                validated_emails.append(raw_email)

        return validated_emails

    def collect_recipients_from_conf():
        print('coletamos os emails para envio definidos na conf: AUDIT_LOG_NOTIFICATION_RECIPIENTS')
        recipients_from_conf = current_app.config['AUDIT_LOG_NOTIFICATION_RECIPIENTS']
        recipients_from_conf_validated = filter_only_valid_emails(recipients_from_conf)
        print('emails definidos na configuração, validados: ', recipients_from_conf_validated)
        if len(recipients_from_conf_validated) == 0:
            print('não temos emails (da configuração) válidos, para enviar')
        return recipients_from_conf_validated

    def colect_recipiets_from_users_table():
        active_users = webapp.dbsql.session.query(models.User).filter_by(email_confirmed=True)
        print('recipients_from_users: ', [u.email for u in active_users])
        return [u.email for u in active_users]

    def prepare_report_email(recipients, records):
        report_date = datetime.today().strftime('%Y-%m-%d')
        collection_acronym = current_app.config['OPAC_COLLECTION']
        email_subject = '[%s] - Relatório de auditoria de mudanças - últimas 24hs (%s) ' % (collection_acronym, report_date)
        templ_context = {
            'records': records,
            'report_date': report_date
        }
        email_data = {
            'recipient': recipients,
            'subject': email_subject,
            'html': render_template("admin/email/audit_log_report.html", **templ_context)
        }
        return email_data

    flask_app = webapp.create_app()

    with flask_app.app_context():
        if current_app.config['AUDIT_LOG_NOTIFICATION_ENABLED']:

            target_datetime = datetime.today() - timedelta(days=1)
            date_range_query = {
                "created_at": {
                    '$gte': target_datetime
                }
            }

            audit_records = AuditLogEntry.objects.filter(__raw__=date_range_query).order_by('-created_at')
            audit_records_count = audit_records.count()
            if audit_records_count > 0:
                print("registros encontrados: ", audit_records_count)
                recipients_from_conf_validated = collect_recipients_from_conf()
                recipients_from_users = colect_recipiets_from_users_table()
                all_recipients = recipients_from_conf_validated + recipients_from_users
                print('todos os recipients:', all_recipients)

                for record in audit_records:
                    print('-> ', record._id, record.created_at.strftime('%Y-%m-%d %H:%M:%S'))

                email_data = prepare_report_email(all_recipients, audit_records)
                send_email(**email_data)
            else:
                print("não encontramos registros modifiados hoje.")
        else:
            print('O envio de email de auditoria esta desativado. Verifique a conf: AUDIT_LOG_NOTIFICATION_ENABLED')
