# coding=utf-8

import os
import logging

from bs4 import BeautifulSoup, Comment, element
from slugify import slugify


LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'DEBUG')
logging.basicConfig(level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)
fh = logging.FileHandler('journal_pages.log', mode='w')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


PAGE_NAMES = ['iaboutj.htm',
              'iedboard.htm',
              'iinstruc.htm',
              'paboutj.htm',
              'pedboard.htm',
              'pinstruc.htm',
              'eaboutj.htm',
              'eedboard.htm',
              'einstruc.htm',
              ]

PAGE_NAMES_BY_LANG = {
    'en': ['iaboutj.htm',
           'iedboard.htm',
           'iinstruc.htm'],
    'pt_BR': ['paboutj.htm',
              'pedboard.htm',
              'pinstruc.htm'],
    'es': ['eaboutj.htm',
           'eedboard.htm',
           'einstruc.htm'],
}


class JournalStaticPageFile(object):

    # about, editors, instructions, contact
    # 'iaboutj.htm', 'iedboard.htm', 'iinstruc.htm'
    anchors = {
        'about': 'aboutj',
        'editors': 'edboard',
        'instructions': 'instruc',
    }
    versions = {'p': 'português', 'e': 'español', 'i': 'English'}
    h1 = {
        'paboutj.htm': 'Sobre o periódico',
        'pedboard.htm': 'Corpo Editorial',
        'pinstruc.htm': 'Instruções aos autores',
        'eaboutj.htm': 'Acerca de la revista',
        'eedboard.htm': 'Cuerpo Editorial',
        'einstruc.htm': 'Instrucciones a los autores',
        'iaboutj.htm': 'About the journal',
        'iedboard.htm': 'Editorial Board',
        'iinstruc.htm': 'Instructions to authors',
    }

    PT_UNAVAILABLE_MSG = 'Informação não disponível em português. ' + \
                         'Consultar outra versão. '
    ES_UNAVAILABLE_MSG = 'Información no disponible en español. ' + \
                         'Consultar otra versión. '

    def __init__(self, original_website, filename):
        self.original_website = original_website
        self.acron = os.path.basename(os.path.dirname(filename))
        self.filename = filename
        self.name = os.path.basename(filename)
        self.version = self.versions[self.name[0]]
        self.file_content = self._read()
        self.get_tree()

    def get_tree(self):
        """
        Obter árvore de um arquivo experimentando os parsers nesta ordem:
        lxml e html.parser. Depedendo do arquivo e/ou parser a árvore é gerada
        incompleta.
        """
        for parser in ['lxml', 'html.parser']:
            if parser is not None:
                self.tree = BeautifulSoup(self.file_content, parser)
            if self.middle_end_insertion_position is None:
                self._info('Not found: end. FAILED {}'.format(parser))
            elif self.middle_begin_insertion_position is None:
                self._info('Not found: begin. FAILED {}'.format(parser))
            else:
                break

    @property
    def anchor_title(self):
        title = self.h1.get(self.name)
        if title is None:
            alt = [v for k, v in self.h1.items()
                   if self.name[:5] == k[:5]]
            if len(alt) == 1:
                title = alt[0]
        return '<h1>{}</h1>'.format(title or '')

    @property
    def _body_tree(self):
        if self.tree is not None:
            if self.tree.body is not None:
                return self.tree.body
        return self.tree

    @property
    def tree_content(self):
        if self.tree is None:
            return self.file_content
        return str(self.tree)

    @property
    def body_content(self):
        if self._body_tree is not None:
            return str(self._body_tree)

    def _info(self, msg):
        logger.debug('%s %s' % (self.filename, msg))

    def _read(self):
        _content = None
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                _content = f.read()
        except UnicodeError:
            with open(self.filename, 'r', encoding='iso-8859-1') as f:
                _content = f.read()
                self._info('iso-8859-1')
        except Exception as e:
            self._info(u'%s' % e)
            logging.error(u'%s' % e)
        return _content or ''

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

    @property
    def original_journal_home_page(self):
        return '{}/{}'.format(self.original_website, self.acron)

    @property
    def new_journal_home_page(self):
        return '/journal/{}/'.format(self.acron)

    def new_about_journal_page(self, anchor):
        return self.new_journal_home_page+'about/#'+anchor

    def new_author_page(self, old_page):
        if 'exprSearch=' in old_page:
            name = old_page[old_page.rfind('exprSearch=')+len('exprSearch='):]
            if '&' in name:
                name = name[:name.find('&')]
            return '//search.scielo.org/?q=au:{}'.format(
                name.replace(' ', '+')
            )
        return old_page

    def remove_original_website_location(self):
        for elem_name, attr_name in [('a', 'href'), ('img', 'src')]:
            for elem in self.get_original_website_reference(
                    elem_name, attr_name):
                url = elem[attr_name]
                if url.lower().endswith(self.original_journal_home_page):
                    elem[attr_name] = self.new_journal_home_page
                elif url.endswith('.htm') and '/{}/'.format(self.acron) in url:
                    for new, old in self.anchors.items():
                        if old in url:
                            elem[attr_name] = self.new_about_journal_page(new)
                elif 'cgi-bin' in url and 'indexSearch=AU' in url:
                    elem[attr_name] = self.new_author_page(url)
                elif self.original_website in url:
                    p = url.find(self.original_website) + \
                        len(self.original_website)
                    elem[attr_name] = url[p:]
                if elem[attr_name] != url:
                    self.fix_elem_string(elem, attr_name, url)

    def fix_elem_string(self, elem, attr_name, url):
        if elem.string is not None:
            elem_string = elem.string.strip().replace('&nbsp;', '')
            if elem_string == url:
                elem.string = '{}{}'.format(
                    self.original_website,
                    elem.string.replace(url, elem[attr_name]))
            elif url.endswith(elem_string):
                elem.string = '{}{}'.format(
                    self.original_website, elem[attr_name])

    def get_original_website_reference(self, elem_name, attribute_name):
        mentions = []
        for item in self._body_tree.find_all(elem_name):
            value = item.get(attribute_name, '')
            if self.original_website in value:
                mentions.append(item)
        return mentions

    def _remove_anchors(self):
        items = self._body_tree.find_all('a')
        for item in items:
            name = item.get('name')
            if name is not None:
                if item.string:
                    item.insert_after(item.string)
                item.extract()

    def _insert_bold_to_p_subtitulo(self):
        p_items = self._body_tree.find_all('p')
        for p in p_items:
            style = p.get('class')
            if style is not None:
                if 'subtitulo' in list(style):
                    if not p.find_all('b'):
                        del p['class']
                        for item in p.children:
                            new_tag = self.tree.new_tag("b")
                            wrap(item, new_tag)

    def find_p_middle_begin(self):
        """
        Localiza no texto <p id="middle_begin"/> que é a posição que indica
        início do bloco de texto principal
        """
        items = [p
                 for p in self._body_tree.find_all('p')
                 if p.get('id', '') == 'middle_begin']
        if len(items) == 1:
            return items[0]

    def insert_p_middle_begin(self):
        """
        Insere no texto <p id="middle_begin"/> que é a posição que indica
        início do bloco de texto principal
        """
        table = self.middle_begin_insertion_position
        if table is not None:
            new_tag = self.tree.new_tag("p")
            new_tag['id'] = 'middle_begin'
            table.insert_after(new_tag)
            return new_tag

    @property
    def p_middle_begin(self):
        """
        Recupera <p id="middle_begin"/> que é a posição que indica
        início do bloco de texto principal.
        Cria <p id="middle_begin"/> se não existe.
        """
        p = self.find_p_middle_begin()
        if p is None:
            return self.insert_p_middle_begin()
        return p

    @property
    def middle_begin_insertion_position(self):
        """
        Identifica a posição de inserção de <p id="middle_begin"/>
        que é a posição que indica início do bloco de texto principal.
        """
        table = self._body_tree.find('table')
        if table is not None:
            header = str(table)
            if has_header(header):
                return table

    def find_p_middle_end(self):
        """
        Localiza no texto <p id="middle_end"/> que é a posição que indica
        fim do bloco de texto principal
        """
        items = [p
                 for p in self._body_tree.find_all('p')
                 if p.get('id', '') == 'middle_end']
        if len(items) == 1:
            return items[0]

    def insert_p_middle_end(self):
        """
        Insere no texto <p id="middle_end"/> que é a posição que indica
        fim do bloco de texto principal
        """
        p = self.middle_end_insertion_position
        if p is not None:
            new_tag = self.tree.new_tag("p")
            new_tag['id'] = 'middle_end'
            p.insert_before(new_tag)
            return new_tag

    @property
    def p_middle_end(self):
        """
        Recupera <p id="middle_end"/> que é a posição que indica
        fim do bloco de texto principal.
        Cria <p id="middle_end"/> se não existe.
        """
        p = self.find_p_middle_end()
        if p is None:
            return self.insert_p_middle_end()
        return p

    @property
    def middle_end_insertion_position(self):
        """
        Identifica a posição de inserção de <p id="middle_end"/>
        que é a posição que indica fim do bloco de texto principal.
        """
        p = None
        href_items = []
        a_items = self._body_tree.find_all('a')
        for a in a_items:
            href = a.get('href')
            if href is not None:
                href = str(href).strip()
                href_items.append((a, href, a.text))
                if has_footer(href, a):
                    p = a.parent
                    break
        if p is None:
            for hr in self._body_tree.find_all('hr'):
                p = hr
            if p is not None:
                self._info('footer hr')
        if p is not None:
            return p

    def _get_middle_children_eval_child(self, child, task):
        if task == 'find_p_begin':
            if child == self.p_middle_begin:
                task = 'find_p_end'
            return task, None
        if task == 'find_p_end' and child == self.p_middle_end:
            return 'stop', None
        if isinstance(child, Comment):
            return task, None
        return task, child

    def _get_middle_children(self):
        task = 'find_p_begin'
        items = []
        for child in self._body_tree.children:
            task, item = self._get_middle_children_eval_child(child, task)
            if item is not None:
                items.append(item)
            elif task == 'stop':
                break
        return items

    @property
    def anchor_name(self):
        for anchor_name, name in self.anchors.items():
            if name in self.filename:
                return anchor_name

    @property
    def anchor(self):
        _anchor = self.anchor_name
        if _anchor is not None:
            return '<a name="{}"> </a>'.format(_anchor)
        return ''

    def _check_unavailable_message(self, content):
        if self.version == 'português' and 'não disponível' in content:
            return self.PT_UNAVAILABLE_MSG
        elif self.version == 'español' and 'no disponible' in content:
            return self.ES_UNAVAILABLE_MSG

    def _get_unavailable_message(self):
        self._unavailable_message = None
        text = self._check_unavailable_message(self.body_content)
        if text:
            p_items = self.sorted_by_relevance
            msg = self._check_unavailable_message(p_items[0][1])
            if msg is not None:
                self._info(len(p_items[0][1]))
                self._info(p_items[0][1][:300])
                if len(p_items[0][1]) < 300:
                    self._unavailable_message = '<p>{}</p>'.format(msg)
                    self._info(self._unavailable_message)
                else:
                    self._info('IGNORED')

    @property
    def sorted_by_relevance(self):
        return sorted([(len(p), p) for p in self.middle_items], reverse=True)

    @property
    def middle_children(self):
        if not hasattr(self, '_middle_children'):
            self._middle_children = self._get_middle_children()
        return self._middle_children

    @property
    def middle_items(self):
        if not hasattr(self, '_middle_items'):
            self._middle_items = [child_tostring(item).strip()
                                  for item in self.middle_children]
        return self._middle_items

    @property
    def middle_text(self):
        if not hasattr(self, '_middle_text'):
            self._middle_text = ''.join([str(item)
                                         for item in self.middle_children])
        return self._middle_text

    @property
    def unavailable_message(self):
        self._get_unavailable_message()
        return self._unavailable_message

    @property
    def img_paths(self):
        _img_paths = []
        for child in self.middle_children:
            if isinstance(child, element.Tag):
                for img in child.find_all('img'):
                    src = img.get('src')
                    if src is not None and '://' not in src:
                        _img_paths.append(src)
        return _img_paths

    def get_alternative_middle_text(self):
        _middle = self.file_content
        for tag_name in ['table', 'p', 'body']:
            for tag in ['<'+tag_name+' ', '<'+tag_name+'>', '</'+tag_name+'>']:
                _middle = _middle.replace(tag.upper(), tag.lower())
        middle = _middle
        if '</table>' in middle:
            middle = middle[middle.find('</table>')+len('</table>'):]
        if 'Home' in middle:
            middle = middle[:middle.rfind('Home')]
            middle = middle[:middle.rfind('<p')]
        elif 'Volver' in middle:
            middle = middle[:middle.rfind('Volver')]
            middle = middle[:middle.rfind('<p')]
        elif 'Voltar' in middle:
            middle = middle[:middle.rfind('Voltar')]
            middle = middle[:middle.rfind('<p')]
        elif '<p class="rodape">' in middle:
            middle = middle[:middle.rfind('<p class="rodape">')]
        elif '://creativecommons.org' in middle:
            middle = middle[:middle.rfind('://creativecommons.org')]
            middle = middle[:middle.rfind('<p')]
        if '</body>' in middle:
            middle = middle[:middle.rfind('</body>')]
        middle = middle.strip()
        self._info('BEGIN:')
        self._info(middle[:100])
        self._info('END:')
        self._info(middle[-100:])
        self._info('REMOVED BEGIN:')
        self._info(_middle[:_middle.find(middle)])
        self._info('REMOVED END:')
        self._info(_middle[_middle.find(middle)+len(middle):])

        return middle

    def remove_p_in_li(self):
        for li in self._body_tree.find_all('li'):
            p = li.find('p')
            if p is not None:
                p.unwrap()

    @property
    def middle(self):
        self.remove_original_website_location()
        self.remove_p_in_li()
        self._remove_anchors()
        self._insert_bold_to_p_subtitulo()
        if self.p_middle_end is None:
            return self.get_alternative_middle_text()
        return self.middle_text

    @property
    def body(self):
        return '<!-- inicio {} -->'.format(self.filename) + \
               self.anchor + self.anchor_title + \
               self.middle + '<hr noshade="" size="1"/>' + \
               '<!-- fim {} -->'.format(self.filename)


class JournalNewPages(object):

    def __init__(self, original_website, revistas_path, img_revistas_path, acron):
        self.original_website = original_website
        self.revistas_path = revistas_path
        self.img_revistas_path = img_revistas_path
        self.acron = acron
        self.journal_pages_path = os.path.join(revistas_path, acron)
        self.used_names = {}

    def get_new_journal_page(self, files):
        """
        Extract the header and the footer of the page
        Insert the anchor based on filename
        """
        content = []
        img_paths = []
        unavailable_message = None
        for file in files:
            file_path = os.path.join(self.journal_pages_path, file)
            page = JournalStaticPageFile(
                self.original_website, file_path)
            if page.unavailable_message:
                content.append(page.anchor)
                unavailable_message = page.unavailable_message
            else:
                content.append(page.body)
                img_paths.extend(page.img_paths)
        if unavailable_message is not None:
            content.append(unavailable_message)
        return '\n'.join(content), sorted(list(set(img_paths)))

    def _find_journal_page_img_file(self, img_in_file):
        img_basename = os.path.basename(img_in_file)
        location = os.path.join(self.journal_pages_path, img_basename)
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

    def _img_new_name(self, img_location):
        img_basename = os.path.basename(img_location)
        img_name, img_ext = os.path.splitext(img_basename)
        if img_location is not None:
            alt_name = slugify(img_name) + img_ext
            if self.used_names.get(alt_name) in [None, img_basename]:
                new_img_name = alt_name
            else:
                new_img_name = img_basename
            self.used_names[new_img_name] = img_basename
            return new_img_name

    def get_journal_page_img_paths(self, images_in_file):
        images = []
        for img_in_file in sorted(list(set(images_in_file))):
            img_location = self._find_journal_page_img_file(img_in_file)
            if img_location is not None:
                new_img_name = self._img_new_name(img_location)
                img_dest_name = '%s_%s' % (self.acron, new_img_name)
                images.append((img_in_file, img_location, img_dest_name))
        return images


def has_header(content):
    return 'Editable' in content and '<!--' in content and '-->' in content or\
           'href="#0' in content or \
           'script=sci_serial' in content or \
           '/scielo.php?lng=' in content


def has_footer(href, a=None):
    if a is not None:
        return '#' == href and a.text.strip() == 'Home' or \
               'script=sci_serial' in href and a.text.strip() == 'Home' or \
               'script=sci_serial' in href and a.text.strip() == 'Voltar' or \
               'script=sci_serial' in href and a.text.strip() == 'Volver' or \
               'javascript:history.back()' == href
    return 'script=sci_serial' in href and 'Home' in href or \
           'script=sci_serial' in href and 'Voltar' in href or \
           'script=sci_serial' in href and 'Volver' in href or \
           'javascript:history.back()' in href


def remove_exceding_space_chars(content):
    parts = content.split()
    return ' '.join([p for p in parts if len(p) > 0])


def child_tostring(child):
    if isinstance(child, element.Tag):
        return child.text
    elif isinstance(child, element.NavigableString):
        return child


def wrap(child, new_tag):
    if isinstance(child, element.Tag):
        if child.string is not None:
            child.wrap(new_tag)
    elif isinstance(child, element.NavigableString):
        return child.wrap(new_tag)


def get_acron_list(REVISTAS_PATH):
    acron_list = []
    for item in os.listdir(REVISTAS_PATH):
        path = os.path.join(REVISTAS_PATH, item)
        if os.path.isdir(path):
            if set(PAGE_NAMES) & set(os.listdir(path)) == set(PAGE_NAMES):
                acron_list.append(item)
    return acron_list


def generate_journals_pages(REVISTAS_PATH, IMG_REVISTAS_PATH, acron_list=None):
    if acron_list is None:
        acron_list = get_acron_list(REVISTAS_PATH)
    not_found = []
    images = []
    RESULTADO = REVISTAS_PATH+'_new'
    if not os.path.isdir(RESULTADO):
        os.makedirs(RESULTADO)
    for acron in acron_list:
        pages_source = JournalNewPages('www.scielo.br', REVISTAS_PATH,
                                               IMG_REVISTAS_PATH, acron)
        for lang, files in PAGE_NAMES_BY_LANG.items():
            content, images_in_file = pages_source.get_new_journal_page(files)
            if content:
                journal_img_paths = pages_source.get_journal_page_img_paths(
                                                images_in_file)
                resultado = '{}/{}_{}.html'.format(RESULTADO, acron, lang)
                with open(resultado, 'w') as f:
                    f.write(content)
            if len(journal_img_paths) < len(images_in_file):
                _found = [item[0] for item in journal_img_paths]
                for img_in_file in images_in_file:
                    if img_in_file not in _found:
                        not_found.append((acron, lang, img_in_file))
            images.extend(images_in_file)
    open('images_in_file.txt', 'w').write(
            '\n'.join(sorted(list(set(images)))))
    open('images_not_found.log', 'w').write(
            '\n'.join([str(item) for item in not_found]))


if __name__ == '__main__':
    import sys
    paths = [item for item in sys.argv[1:3] if os.path.isdir(item)]
    if len(paths) == 2:
        generate_journals_pages(paths[0], paths[1])
    else:
        print('Usage: python journal_static_page.py revistas img_revistas')
