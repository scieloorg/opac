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
        # http://www.scielo.br/cgi-bin/wxis.exe/iah/
        # ?IsisScript=iah/iah.xis&base=article%5Edlibrary&format=iso.pft&
        # lang=p&nextAction=lnk&
        # indexSearch=AU&exprSearch=MEIERHOFFER,+LILIAN+KOZSLOWSKI
        # ->
        # //search.scielo.org/?q=au:MEIERHOFFER,+LILIAN+KOZSLOWSKI')
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
                    elem.string = self.link_display_text(
                        elem[attr_name], elem.string, old_url)

        replacements = set(list(replacements))
        for old, new in replacements:
            if self.body.count(old) > 0:
                logging.info(
                    'CONFERIR: ainda existe: {} ({})'.format(
                        old, self.body.count(old)))

    def fix_invalid_url(self, elem, attr_name):
        pass

    def replace_by_relative_url(self, url):
        # www.scielo.br/revistas/icse/levels.pdf -> /revistas/icse/levels.pdf
        #
        # www.scielo.br/img/revistas/icse/levels.pdf ->
        # /img/revistas/icse/levels.pdf
        #
        # http://www.scielo.br/scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso
        # -> /scielo.php?script=sci_serial&pid=0102-4450&lng=en&nrm=iso
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
        return url

    def get_new_url(self, url):
        if url.strip().count(' ') > 0:
            return url

        if 'cgi-bin' in url and 'indexSearch=AU' in url:
            return self.new_author_page(url)

        if self.original_website in url:
            return self.replace_by_relative_url(url)
        return url

    def link_display_text(self, link, display_text, original_url):
        if display_text is not None:
            text = display_text.strip().replace('&nbsp;', '')
            if text == original_url:
                return '{}{}'.format(self.original_website,
                                     text.replace(original_url, link))
            elif original_url.endswith(text):
                return '{}{}'.format(self.original_website, link)
        return display_text

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

    def guess_file_location(self, file_path):
        if '/img/revistas/' in file_path:
            return os.path.join(
                self.img_revistas_path,
                file_path[file_path.find('/img/revistas/') +
                          len('/img/revistas/'):])
        if '/revistas/' in file_path:
            return os.path.join(
                self.revistas_path,
                file_path[file_path.find('/revistas/') +
                          len('/revistas/'):])
        if self.page_path:
            if self.original_website in file_path:
                location = file_path[file_path.find(self.original_website) +
                                     len(self.original_website):]
                return os.path.join(self.page_path, location[1:])
            elif file_path.startswith('/'):
                location = file_path[1:]
                return os.path.join(self.page_path, location)

    def confirm_file_location(self, file_location, file_path):
        try:
            # Verifica se a imagem existe
            open(file_location)
        except IOError as e:
            logging.error(
                u'%s (corresponding to %s)' % (e, file_path))
        else:
            return file_location

    def get_slug_name(self, file_location):
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

    @property
    def prefixes(self):
        return [self.page_name, self.lang]

    def add_prefix_to_slug_name(self, new_img_name):
        _prefixes = self.prefixes + [new_img_name]
        parts = [part for part in _prefixes if part is not None]
        return '_'.join(parts)

    def get_image_info(self, img_in_file):
        img_location = self.guess_file_location(img_in_file)
        if self.confirm_file_location(img_location, img_in_file):
            new_img_name = self.get_slug_name(img_location)
            img_dest_name = self.add_prefix_to_slug_name(new_img_name)
            return (img_in_file, img_location, img_dest_name)

    def create_images(self, images=None):
        for image in images or self.images:
            # interna ou externa
            src = image.get('src')
            if ':' not in src:
                # interno
                self.register_image(image)

    def register_image(self, image):
        image_info = self.get_image_info(image.get('src'))
        if image_info:
            img_in_file, img_src, img_dest = image_info
            img = create_image(
                img_src, img_dest, check_if_exists=False)
            image['src'] = img.get_absolute_url



class JournalPage(Page):

    def __init__(self, content, original_website, revistas_path,
                 img_revistas_path, acron,
                 page_path=None, page_name=None, lang=None):
        super().__init__(content, original_website, revistas_path,
                         img_revistas_path, page_path, page_name, lang)
        self.acron = acron

    @property
    def prefixes(self):
        return [self.acron]

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
            return url

        # www.scielo.br/icse -> /journal/icse/
        if url.lower().endswith(self.original_journal_home_page):
            return self.new_journal_home_page

        # www.scielo.br/revistas/icse/iaboutj.htm -> /journal/icse/about/#about
        if url.endswith('.htm') and '/{}/'.format(self.acron) in url:
            for new, old in self.anchors.items():
                if old in url:
                    return self.new_about_journal_page(new)

        if 'cgi-bin' in url and 'indexSearch=AU' in url:
            return self.new_author_page(url)

        if self.original_website in url:
            return self.replace_by_relative_url(url)
        return url
