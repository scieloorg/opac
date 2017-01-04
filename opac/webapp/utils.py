# coding: utf-8

import os
import pytz
import shutil
import feedparser
import datetime
from werkzeug import secure_filename
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import current_app, url_for
from . import controllers
from . import models
import webapp
import re
import requests

try:
    from PIL import Image
except ImportError:
    Image = None

CSS = "/static/css/style_article_html.css"  # caminho para o CSS a ser incluído no HTML do artigo
REGEX_EMAIL = re.compile(r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", re.IGNORECASE)  # RFC 2822 (simplified)


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
    A lista de fascículos é ordenada pelos fascículos mais recentes para o mais
    antigos, portanto para retornarmos os fascículos mais antigos, devemos
    caminhar pelo índice do valor menor para o maior, isso justifica
    no preview soma 1 ao índice.

    param: issues é a lista de issue (deve ser ordenado do fascículo mais
    recente para o mais antigo)
    param: issue é o issue corrente.

    IMPORTANTE: A lista de fascículos deve ter mais do que 1 item para que
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
    A lista de fascículos é ordenada pelos fascículos mais recentes para o mais
    antigos, portanto para retornarmos os fascículos mais novos, devemos
    caminhar pelo índice do valor maior para o menor, isso justifica
    no preview subtrai 1 ao índice.

    param: issues é a lista de issue (deve ser ordenado do fascículo mais
    recente para o mais antigo)
    param: issue é o issue corrente.

    IMPORTANTE: A lista de fascículos deve ter mais do que 1 item para que
    possa existir a ideia de anterior e próximo
    """

    if len(issues) >= 2:
        try:
            # Caso o fascículo seja o primeiro retorna None
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
        password=user_password,
        email_confirmed=user_email_confirmed)
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
    except Exception as e:
        print(e)
    else:
        return image_path


def create_image(image_path, filename):
    """
    Função que cria uma imagem para o modelo Image.

    Parâmento image_path caminho absoluto para a imagem.
    Parâmento filename no para o arquivo com extensão.
    """

    image_root = current_app.config['IMAGE_ROOT']

    image_destiation_path = os.path.join(image_root, filename)

    try:
        shutil.copyfile(image_path, image_destiation_path)
    except IOError as e:
        # https://docs.python.org/3/library/exceptions.html#FileNotFoundError
        print("ERROR: %s" % e)

    generate_thumbnail(image_destiation_path)

    img = models.Image(name=namegen_filename(filename), path='images/' + filename)

    webapp.dbsql.session.add(img)
    webapp.dbsql.session.commit()

    return img


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


def import_feed(feed_url, language):

    def get_item_date(item):
        if 'published_parsed' in list(item.keys()):
            return datetime.datetime(*item.published_parsed[:7])
        else:
            return datetime.datetime.now()

    feed = feedparser.parse(feed_url)

    if feed.bozo == 1:
        msg = 'Não é possível parsear o feed (%s), possívelmente esteja malformado.' % feed_url
        return (False, msg)
    elif len(feed.entries) == 0:
        msg = 'No tem entries para importar.'
        return (True, msg)
    else:
        entries = feed['items']
        entries_count = 0
        for item in entries:
            news_data = {
                # '_id': item.get('id', None),
                'url': item.link,
                'image_url': url_for('static', filename='img/fallback_image.png', _external=True),
                'publication_date': get_item_date(item),
                'title': item.title[:256],
                'description': item.summary,
                'language': language,  # ignoramos o language do feed pq vem errado
            }
            controllers.create_news_record(news_data)
            entries_count += 1
        return (True, entries_count)


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
