# coding=utf-8

import os
import logging

from bs4 import BeautifulSoup, Comment, element


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('journal_pages.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


class JournalStaticPage(object):

    # about, editors, instructions, contact
    # 'iaboutj.htm', 'iedboard.htm', 'iinstruc.htm'
    anchors = {
        'about': 'about',
        'editors': 'edboard',
        'instructions': 'instruc',
    }

    def __init__(self, filename, content):
        self.filename = filename
        self.content = content

    @property
    def header(self):
        _header = None
        if '<table' in self.content:
            _header = self.content[self.content.find('<table'):]
            _header = _header[:_header.find('</table>')+len('</table>')]
            _header = _header.strip()
            if _header.startswith('<table') and _header.endswith('</table>'):
                pass
            else:
                print(self.filename, 'header', 'unexpected format')
                _header = None
        return _header

    @property
    def footer(self):
        _footer = None
        if 'script=sci_serial' in self.content:
            p = self.content.rfind('script=sci_serial')
            _footer = self.content[:p]
            p = _footer.rfind('<p ')
            _footer = self.content[p:]
            _footer = _footer[:_footer.find('</body>')]
            _footer = _footer.strip()
            if _footer.startswith('<p') and _footer.endswith('</p>'):
                pass
            else:
                print(self.filename, 'footer', 'unexpected format')
                _footer = None
        return _footer

    @property
    def anchor(self):
        _anchor = None
        for anchor_name, name in self.anchors.items():
            if name in self.filename:
                _anchor = anchor_name
                break
        if _anchor is not None:
            return '<a name="{}">'.format(_anchor)
        return ''

    @property
    def body(self):
        if all([self.header, self.footer]):
            new = self.content.replace(self.header, self.anchor)
            new = new.replace(self.footer, '<hr noshade="" size="1"/>')
            return new
        return self.content


class JournalStaticPageFile(object):

    # about, editors, instructions, contact
    # 'iaboutj.htm', 'iedboard.htm', 'iinstruc.htm'
    anchors = {
        'about': 'about',
        'editors': 'edboard',
        'instructions': 'instruc',
    }
    versions = {'p': 'português', 'e': 'español', 'i': 'English'}
    PT_UNAVAILABLE_MSG = 'Informação não disponível em português. ' + \
                         'Consultar outra versão. '
    ES_UNAVAILABLE_MSG = 'Información no disponible en español. ' + \
                         'Consultar otra versión. '

    def __init__(self, filename):
        self.filename = filename
        self.name = os.path.basename(filename)
        self.version = self.versions[self.name[0]]
        self.file_content = self._read()
        self.tree = BeautifulSoup(self.file_content, 'lxml')

    @property
    def _body_tree(self):
        if self.tree.body is not None:
            return self.tree.body
        return self.tree

    @property
    def content(self):
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

    def _indicate_middle_begin(self):
        new_tag = self.tree.new_tag("p")
        new_tag['id'] = 'middle_begin'
        table = self._body_tree.find('table')
        if table is not None:
            header = str(table)

            if 'Editable' in header and '<!--' in header and '-->' in header or \
               'href="#0' in header or \
               'script=sci_serial' in header or \
               '/scielo.php?lng=' in header:
                table.insert_after(new_tag)
                return new_tag
        self._info('no header found.')

    def _indicate_middle_end(self):
        p = None
        href_items = []
        a_items = self._body_tree.find_all('a')
        for a in a_items:
            href = a.get('href')
            if href is not None:
                href = str(href).strip()
                href_items.append((a, href, a.text))
                if 'script=sci_serial' in href and a.text.strip() == 'Home' or \
                   'javascript:history.back()' == href:
                    p = a.parent
                    break
        if p is not None:
            new_tag = self.tree.new_tag("p")
            new_tag['id'] = 'middle_end'
            p.insert_before(new_tag)
            return new_tag
        self._info('no footer found.')

    def _get_middle_children_eval_child(self, child, p_begin, p_end, task):
        if task == 'find_p_begin':
            if child == p_begin:
                task = 'find_p_end'
            return task, None
        if task == 'find_p_end' and child == p_end:
            return 'stop', None
        if isinstance(child, Comment):
            return task, None
        return task, child

    def _get_middle_children(self, p_begin, p_end):
        task = 'find_p_begin'
        items = []
        for child in self._body_tree.children:
            task, item = self._get_middle_children_eval_child(
                child, p_begin, p_end, task)
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
                self._unavailable_message = '<p>{}</p>'.format(msg)
            self._info(p_items[0][1])

    @property
    def sorted_by_relevance(self):
        return sorted([(len(p), p) for p in self.middle_items], reverse=True)

    @property
    def middle_children(self):
        if not hasattr(self, '_middle_children'):
            self._remove_anchors()
            self._insert_bold_to_p_subtitulo()
            begin = self._indicate_middle_begin()
            end = self._indicate_middle_end()
            self._middle_children = self._get_middle_children(begin, end)
        return self._middle_children

    @property
    def middle_items(self):
        if not hasattr(self, '_middle_items'):
            self._middle_items = [tostring(item)
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
    def body(self):
        return '<!-- inicio {} -->'.format(self.filename) + \
               self.anchor + self.middle_text + '<hr noshade="" size="1"/>' + \
               '<!-- fim {} -->'.format(self.filename)


def tostring(child):
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
