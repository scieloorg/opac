# coding=utf-8

import os
import logging


from webapp.utils import create_image  # noqa


from bs4 import BeautifulSoup
from slugify import slugify


LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'DEBUG')
logging.basicConfig(level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)
fh = logging.FileHandler('page.log', mode='w')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


class Page(object):

    def __init__(self, content, original_website, revistas_path,
                 img_revistas_path, page_path=None, page_name=None, lang=None):
        self.original_website = original_website
        self.revistas_path = revistas_path
        self.img_revistas_path = img_revistas_path
        self.page_path = page_path
        self.lang = lang
        self.page_name = page_name
        self.content = content
        self.used_names = {}

    @property
    def content(self):
        return str(self.tree)

    @content.setter
    def content(self, value):
        self.tree = BeautifulSoup(value, 'lxml')

    def _info(self, msg):
        logger.debug('%s %s' % (self.filename, msg))

    @property
    def original_website(self):
        return self._original_website

    @original_website.setter
    def original_website(self, value):
        website = value
        if '//' in website:
            website = website[website.find('//')+2:]
        if website.endswith('/'):
            website = website[:-1]
        self._original_website = website

    def new_author_page(self, old_page):
        if 'exprSearch=' in old_page:
            name = old_page[old_page.rfind('exprSearch=')+len('exprSearch='):]
            if '&' in name:
                name = name[:name.find('&')]
            return '//search.scielo.org/?q=au:{}'.format(
                name.replace(' ', '+')
            )
        return old_page

    def migrate_urls_to_new_website(self):
        replacements = []
        for elem_name, attr_name in [('a', 'href'), ('img', 'src')]:
            for elem in self.find_original_website_reference(
                    elem_name, attr_name):
                self.fix_invalid_url(elem, attr_name)
                old_url = elem[attr_name]
                elem[attr_name] = self.get_new_url(old_url)
                if elem[attr_name] != old_url:
                    replacements.append((old_url, elem[attr_name]))
                    self.fix_elem_string(elem, attr_name, old_url)
        replacements = set(list(replacements))
        for old, new in replacements:
            if self.body.count(old) > 0:
                self._info(
                    'CONFERIR: ainda existe: {} ({})'.format(
                        old, self.body.count(old)))

    def fix_invalid_url(self):
        pass

    def get_new_url(self, url):
        if url.strip().count(' ') > 0:
            self._info('CONFERIR: URL MANTIDA | INVALID URL {} {}'.format(
                        url, self.filename))
            return url

        # http://www.scielo.br/cgi-bin/wxis.exe/iah/
        # ?IsisScript=iah/iah.xis&base=article%5Edlibrary&format=iso.pft&
        # lang=p&nextAction=lnk&
        # indexSearch=AU&exprSearch=MEIERHOFFER,+LILIAN+KOZSLOWSKI
        # ->
        # //search.scielo.org/?q=au:MEIERHOFFER,+LILIAN+KOZSLOWSKI')
        if 'cgi-bin' in url and 'indexSearch=AU' in url:
            return self.new_author_page(url)

        # www.scielo.br/revistas/icse/levels.pdf -> /revistas/icse/levels.pdf
        #
        # www.scielo.br/img/revistas/icse/levels.pdf ->
        # /img/revistas/icse/levels.pdf
        #
        # http://www.scielo.br/scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso
        # ->
        # /scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso
        #
        # http://www.scielo.br -> /
        if self.original_website in url:
            p = url.find(self.original_website) + len(self.original_website)
            relative_url = url[p:].strip()
            for relative in ['/scielo.php', '/fbpe', '/revistas',
                             '/img/revistas']:
                if relative_url.startswith(relative):
                    return relative_url
                if relative_url in ["", '/']:
                    return '/'
            self._info('CONFERIR: URL MANTIDA {} {} {}'.format(
                        url, relative_url, self.filename))
        return url

    def fix_elem_string(self, elem, attr_name, original_url):
        if elem.string is not None:
            elem_string = elem.string.strip().replace('&nbsp;', '')
            if elem_string == original_url:
                elem.string = '{}{}'.format(
                    self.original_website,
                    elem.string.replace(original_url, elem[attr_name]))
            elif original_url.endswith(elem_string):
                elem.string = '{}{}'.format(
                    self.original_website, elem[attr_name])

    def find_original_website_reference(self, elem_name, attribute_name):
        mentions = []
        for item in self.tree.find_all(elem_name):
            value = item.get(attribute_name, '')
            if self.original_website in value:
                mentions.append(item)
        return mentions

    @property
    def images(self):
        return [img
                for img in self.tree.find_all('img')
                if img.get('src')]

    def find_image_file_location(self, image):
        img_in_file = image.get('src')
        img_basename = os.path.basename(img_in_file)

        location = img_basename
        if self.page_path:
            location = os.path.join(self.page_path, img_basename)
        if not os.path.isfile(location):
            if '/img/revistas/' in img_in_file:
                location = os.path.join(
                    self.img_revistas_path,
                    img_in_file[img_in_file.find('/img/revistas/') +
                                len('/img/revistas/'):])
            elif '/revistas/' in img_in_file:
                location = os.path.join(
                    self.revistas_path,
                    img_in_file[img_in_file.find('/revistas/') +
                                len('/revistas/'):])
        try:
            # Verifica se a imagem existe
            open(location)
        except IOError as e:
            logging.error(
                u'%s (corresponding to %s)' % (e, img_in_file))
        else:
            return location

    def get_new_file_name(self, file_location):
        file_basename = os.path.basename(file_location)
        file_name, file_ext = os.path.splitext(file_basename)
        if file_location is not None:
            alt_name = slugify(file_name) + file_ext
            if self.used_names.get(alt_name) in [None, file_basename]:
                new_file_name = alt_name
            else:
                new_file_name = file_basename
            self.used_names[new_file_name] = file_basename
            return new_file_name

    def get_image_info(self, img_in_file):
        img_location = self.find_image_file_location(img_in_file)
        if img_location is not None:
            new_img_name = self.get_new_file_name(img_location)
            img_dest_name = '%s_%s' % (self.acron, new_img_name)
            return (img_in_file, img_location, img_dest_name)

    def create_images(self, images_in_file):
        for image in images_in_file:
            # interna ou externa
            image_info = self.get_image_info(image.get('src'))
            if image_info:
                img_in_file, img_src, img_dest = image_info
                img = create_image(img_src, img_dest, check_if_exists=False)
            image['src'] = img.get_absolute_url


class JournalPage(Page):

    def __init__(self, content, original_website, revistas_path,
                 img_revistas_path, acron,
                 page_path=None, page_name=None, lang=None):
        super().__init__(content, original_website, revistas_path,
                         img_revistas_path, page_path, page_name, lang)
        self.acron = acron

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
            return self.new_journal_home_page+'about/#'+anchor
        return ''

    def fix_invalid_url(self, elem, attr_name):
        """
        Trocar o padrao:
        http://www.scielo.br/revistas/icse/www1.folha.uol.com.br
        Por:
        http://www1.folha.uol.com.br
        """
        if self.acron:
            invalid_text = '{}/revistas/{}/'.format(
                self.original_website, self.acron)
            if '{}www'.format(invalid_text) in elem[attr_name]:
                elem[attr_name] = elem[attr_name].replace(invalid_text, '')

    def get_new_url(self, url):
        if url.strip().count(' ') > 0:
            self._info('CONFERIR: URL MANTIDA | INVALID URL {} {}'.format(
                        url, self.filename))
            return url

        # www.scielo.br/icse -> /journal/icse/
        if url.lower().endswith(self.original_journal_home_page):
            return self.new_journal_home_page

        # www.scielo.br/revistas/icse/iaboutj.htm -> /journal/icse/about/#about
        if url.endswith('.htm') and '/{}/'.format(self.acron) in url:
            for new, old in self.anchors.items():
                if old in url:
                    return self.new_about_journal_page(new)

        # http://www.scielo.br/cgi-bin/wxis.exe/iah/
        # ?IsisScript=iah/iah.xis&base=article%5Edlibrary&format=iso.pft&
        # lang=p&nextAction=lnk&
        # indexSearch=AU&exprSearch=MEIERHOFFER,+LILIAN+KOZSLOWSKI
        # ->
        # //search.scielo.org/?q=au:MEIERHOFFER,+LILIAN+KOZSLOWSKI')
        if 'cgi-bin' in url and 'indexSearch=AU' in url:
            return self.new_author_page(url)

        # www.scielo.br/revistas/icse/levels.pdf -> /revistas/icse/levels.pdf
        #
        # www.scielo.br/img/revistas/icse/levels.pdf ->
        # /img/revistas/icse/levels.pdf
        #
        # http://www.scielo.br/scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso
        # ->
        # /scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso
        #
        # http://www.scielo.br -> /
        if self.original_website in url:
            p = url.find(self.original_website) + len(self.original_website)
            relative_url = url[p:].strip()
            for relative in ['/scielo.php', '/fbpe', '/revistas',
                             '/img/revistas']:
                if relative_url.startswith(relative):
                    return relative_url
                if relative_url in ["", '/']:
                    return '/'
            self._info('CONFERIR: URL MANTIDA {} {} {}'.format(
                        url, relative_url, self.filename))
        return url

