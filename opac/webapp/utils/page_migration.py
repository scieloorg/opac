# coding=utf-8

import os
import logging
import requests
import tempfile

from urllib.parse import urlparse

from bs4 import BeautifulSoup
from slugify import slugify


LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'DEBUG')
logging.basicConfig(level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)
fh = logging.FileHandler('page_migration.log', mode='w')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


def is_file(file_path):
    name, ext = os.path.splitext(file_path)
    return ext.lower() in ['.pdf', '.html', '.htm', '.jpg', '.png', '.gif']


def new_author_url_page(old_url):
    # http://www.scielo.br/cgi-bin/wxis.exe/iah/
    # ?IsisScript=iah/iah.xis&base=article%5Edlibrary&format=iso.pft&
    # lang=p&nextAction=lnk&
    # indexSearch=AU&exprSearch=MEIERHOFFER,+LILIAN+KOZSLOWSKI
    # ->
    # //search.scielo.org/?q=au:MEIERHOFFER,+LILIAN+KOZSLOWSKI')
    if 'indexSearch=AU' in old_url and 'exprSearch=' in old_url:
        name = old_url[old_url.rfind('exprSearch=')+len('exprSearch='):]
        if '&' in name:
            name = name[:name.find('&')]
        return '//search.scielo.org/?q=au:{}'.format(
            name.replace(' ', '+')
        )
    return old_url


def slugify_filename(file_location, used_names):
    file_basename = os.path.basename(file_location)
    file_name, file_ext = os.path.splitext(file_basename)
    if file_location is not None:
        alt_name = slugify(file_name) + file_ext
        if used_names.get(alt_name) in [None, file_basename]:
            new_file_name = alt_name
        else:
            new_file_name = file_basename
        used_names[new_file_name] = file_basename
        return new_file_name
    return file_basename


def downloaded_file(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            file_path = os.path.join(tempfile.mkdtemp(), os.path.basename(url))
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path
    except requests.exceptions.ConnectionError as e:
        logging.error(
            u'%s (corresponding to %s)' % (e, url))


def confirm_file_location(file_location, file_path):
    if file_location and os.path.isfile(file_location):
        if os.access(file_location, os.R_OK):
            return True
        else:
            logging.error(
                u'Não legível %s (%s)' % (file_location, file_path))
            return False
    logging.info(
        u'Não existe %s (%s)' % (file_location, file_path))
    return False


def delete_file(file_path):
    try:
        # Verifica se a imagem existe
        os.remove(file_path)
    except IOError as e:
        logging.error(
            u'%s (corresponding to %s)' % (e, file_path))
    except Exception as e:
        logging.error(
            u'%s (corresponding to %s)' % (e, file_path))


class PageMigration(object):
    """
    Define os dados/regras para migracao de qualquer página html
    """
    def __init__(self,
                 original_website,
                 revistas_path,
                 img_revistas_path,
                 static_files_path=None):
        self.original_website = original_website
        self.revistas_path = revistas_path
        self.img_revistas_path = img_revistas_path
        self.static_files_path = static_files_path

    @property
    def original_website(self):
        return self._original_website

    @original_website.setter
    def original_website(self, value):
        o = urlparse(value)
        self._original_website = o.netloc or o.path

    def link_display_text(self, link, display_text, original_url):
        if display_text is not None:
            text = display_text.strip().replace('&nbsp;', '')
            if text == original_url:
                return '{}{}'.format(self.original_website,
                                     text.replace(original_url, link))
            elif original_url.endswith(text):
                return '{}{}'.format(self.original_website, link)
        return display_text

    def replace_by_relative_url(self, url):
        # http://www.scielo.br/revistas/icse/levels.pdf
        # -> /revistas/icse/levels.pdf
        #
        # http://www.scielo.br/img/revistas/icse/levels.pdf
        # -> /img/revistas/icse/levels.pdf
        #
        # http://www.scielo.br/scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso
        # -> /scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso
        #
        # http://www.scielo.br -> /
        # www.scielo.br/revistas/icse/levels.pdf
        # -> /revistas/icse/levels.pdf
        #
        # www.scielo.br/img/revistas/icse/levels.pdf
        # -> /img/revistas/icse/levels.pdf
        #
        # www.scielo.br/scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso
        # -> /scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso
        #
        # www.scielo.br -> /
        if url.count(self.original_website) == 1:
            new_url = url.split(self.original_website)[1]
            for relative in ['/scielo.php', '/img/revistas', '/revistas']:
                if relative in new_url:
                    return new_url[new_url.find(relative):]
            if '/fbpe' in new_url:
                return new_url[new_url.find('/fbpe')+len('/fbpe'):]
            return new_url or '/'
        return url

    def get_new_url(self, url):
        if url.strip().count(' ') > 0:
            return url

        if 'cgi-bin' in url and 'indexSearch=AU' in url:
            return new_author_url_page(url)

        if self.original_website in url:
            return self.replace_by_relative_url(url)
        return url

    def get_file_location(self, referenced):
        file_locations = self.get_possible_locations(referenced)
        found = [file_location
                 for file_location in file_locations
                 if os.path.isfile(file_location)]
        if len(found) > 0:
            return found[0]

    def get_possible_locations(self, file_path):
        """
        /img/revistas/fig01.gif -> /volumes/img_revistas/fig01.gif
        /revistas/fig01.gif -> /volumes/revistas/fig01.gif
        http://www.scielo.br/bla/bla.gif -> /volumes/htdocs/bla/bla.gif
        /bla/bla.gif -> /volumes/htdocs/bla/bla.gif
        """
        possible_locations = []
        changes = [
            ('/img/revistas/', self.img_revistas_path),
            ('/revistas/', self.revistas_path),
        ]
        if self.static_files_path:
            changes.append(
                (self.original_website+'/', self.static_files_path),
            )
        for change in changes:
            if change[0] in file_path:
                possible_locations.append(
                    os.path.join(
                        change[1],
                        file_path[file_path.find(change[0]) + len(change[0]):])
                )
                break
            elif file_path.count('/') == 0:
                possible_locations.append(os.path.join(change[1], file_path))
        if self.static_files_path and file_path.startswith('/'):
            possible_locations.append(
                os.path.join(
                    self.static_files_path,
                    file_path[1:])
                )
        return [item.replace('\n', '') for item in set(possible_locations)]

    def is_asset_url(self, referenced):
        if is_file(referenced):
            sep = ''
            if not referenced.startswith('/'):
                sep = '/'
            return 'http://{}{}{}'.format(
                self.original_website, sep, referenced)


class JournalPageMigration:
    """
    Define os dados/regras para migracao de página html de periódico
    """

    anchors = {
        'about': 'aboutj',
        'editors': 'edboard',
        'instructions': 'instruc',
    }

    def __init__(self, original_website, acron):
        self.original_website = original_website
        self.acron = acron
        self.INVALID_TEXT_IN_URL = '{}/revistas/{}/www'.format(
            self.original_website, acron)

    @property
    def original_website(self):
        return self._original_website

    @original_website.setter
    def original_website(self, value):
        o = urlparse(value)
        self._original_website = o.netloc or o.path

    @property
    def original_journal_home_page(self):
        if self.acron:
            return '{}/{}'.format(self.original_website, self.acron)
        return ''

    @property
    def new_journal_home_page(self):
        if self.acron:
            return '/journal/{}/'.format(self.acron)
        return ''

    def new_about_journal_page(self, anchor):
        if self.acron:
            if anchor in self.anchors.keys():
                return self.new_journal_home_page+'about/#'+anchor
            return self.new_journal_home_page+'about'
        return ''

    def _fix_invalid_url(self, url):
        """
        ERRADO: http://www.scielo.br/revistas/icse/www1.folha.uol.com.br
        CORRETO: http://www1.folha.uol.com.br
        """
        if self.INVALID_TEXT_IN_URL and self.INVALID_TEXT_IN_URL in url:
            return url.replace(self.INVALID_TEXT_IN_URL, '')
        return url

    def get_new_url(self, url):
        url = self._fix_invalid_url(url)

        # www.scielo.br/icse -> /journal/icse/
        if url.lower().endswith(self.original_journal_home_page):
            return self.new_journal_home_page

        # www.scielo.br/revistas/icse/iaboutj.htm -> /journal/icse/about/#about
        if url.endswith('.htm') and '/{}/'.format(self.acron) in url:
            for new, old in self.anchors.items():
                if old in url:
                    return self.new_about_journal_page(new)
        return url


class MigratedPage(object):
    """
    Corrigir os links internos
    Registrar os arquivos e imagens
    Corrigir os links internos destes arquivos e imagens
    """
    def __init__(self, migration, content,
                 acron=None, page_name=None, lang=None):
        self.used_names = {}
        self.acron = acron
        self.lang = lang
        self.page_name = page_name
        self.content = content
        if page_name:
            self.prefixes = [page_name, lang]
        else:
            self.prefixes = [acron]
        self.migration = migration
        self.j_migration = None
        if self.acron:
            self.j_migration = JournalPageMigration(
                migration.original_website, acron)

    @property
    def content(self):
        return ''.join([str(content) for content in self.tree.body.contents])

    @content.setter
    def content(self, value):
        self.tree = BeautifulSoup(value, 'lxml')
        if self.acron:
            for item in self.tree.find_all('a'):
                if item.get('href') and is_file(item.get('href')) and \
                        item['href'].count('/') == 0:
                    item['href'] = "/revistas/{}/{}".format(
                        self.acron, item['href'])

    def migrate_urls(self, create_file_function, create_image_function):
        self.fix_urls()
        self.create_files(create_file_function)
        self.create_images(create_image_function)

    def fix_urls(self):
        replacements = []
        for elem_name, attr_name in [('a', 'href'), ('img', 'src')]:
            for elem in self.find_original_website_reference(
                    elem_name, attr_name):
                old_url = str(elem[attr_name])
                new_url = old_url
                if self.j_migration:
                    new_url = self.j_migration.get_new_url(new_url)
                new_url = self.migration.get_new_url(new_url)
                if new_url != old_url:
                    replacements.append((old_url, new_url))
                    old_display_text = elem.string
                    elem[attr_name] = new_url
                    new_display_text = self.migration.link_display_text(
                        new_url, old_display_text, old_url)
                    if new_display_text != old_display_text:
                        elem.string = new_display_text

        replacements = list(sorted(set(replacements)))
        for old, new in replacements:
            q = self.content.count(old)
            if q > 0:
                logging.info(
                    'CONFERIR: ainda existe: {} ({})'.format(old, q))

    def find_original_website_reference(self, elem_name, attribute_name):
        mentions = []
        for item in self.tree.find_all(elem_name):
            value = item.get(attribute_name, '')
            if self.migration.original_website in value:
                mentions.append(item)
        return mentions

    @property
    def images(self):
        return [img
                for img in self.tree.find_all('img')
                if img.get('src')]

    @property
    def files(self):
        return [item
                for item in self.tree.find_all('a')
                if item.get('href') and is_file(item.get('href'))]

    def get_prefixed_slug_name(self, file_path):
        new_name = slugify_filename(file_path, self.used_names)
        _prefixes = self.prefixes
        parts = [slugify(part) for part in _prefixes if part is not None]
        return '_'.join(parts + [new_name])

    def get_file_info(self, referenced):
        file_location = self.migration.get_file_location(referenced)
        valid_path = confirm_file_location(file_location, referenced)
        url = None
        if not valid_path:
            url = self.migration.is_asset_url(referenced)
            if url:
                file_location = downloaded_file(url)
                valid_path = confirm_file_location(file_location, referenced)
        if valid_path:
            file_dest_name = self.get_prefixed_slug_name(file_location)
            return (file_location, file_dest_name, url is not None)
        logging.info('CONFERIR: {} não encontrado'.format(referenced))

    def create_images(self, create_image_function):
        for image in self.images:
            src = image.get('src')
            if ':' not in src:
                image_info = self.get_file_info(src)
                if image_info:
                    img_src, img_dest, is_temp = image_info
                    image['src'] = create_image_function(
                        img_src, img_dest, check_if_exists=False)
                    if is_temp:
                        delete_file(img_src)

    def create_files(self, create_file_function):
        for _file in self.files:
            href = _file.get('href')
            if ':' not in href:
                _file_info = self.get_file_info(href)
                if _file_info:
                    _file_href, _file_dest, is_temp = _file_info
                    _file['href'] = create_file_function(
                        _file_href, _file_dest, check_if_exists=False)
                    if is_temp:
                        delete_file(_file_href)
