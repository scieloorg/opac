# coding=utf-8

import html.parser
import logging

logger = logging.getLogger(__name__)


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
        temp = None
        if 'script=sci_serial' in self.content:
            p = self.content.rfind('script=sci_serial')
            temp = self.content[:p]
            p = temp.rfind('<p ')
            temp = self.content[p:]
            if '</body>' in temp:
                temp = temp[:temp.find('</body>')]
                temp = temp.strip()
            else:
                temp = None
        if temp is None:
            logger.info('%s has unexpected footer format.' % self.filename)
        return temp

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
        new = self.content
        if self.header:
            new = new.replace(self.header, self.anchor)
        if self.footer:
            new = new.replace(self.footer, '<hr noshade="" size="1"/>')
        return new


class JournalStaticPageFile(object):

    # about, editors, instructions, contact
    # 'iaboutj.htm', 'iedboard.htm', 'iinstruc.htm'
    anchors = {
        'about': 'about',
        'editors': 'edboard',
        'instructions': 'instruc',
    }

    def __init__(self, filename):
        self.filename = filename
        self.content = self.read()

    def read(self):
        _content = None
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                _content = f.read()
        except UnicodeError:
            with open(self.filename, 'r', encoding='iso-8859-1') as f:
                _content = f.read()
                logger.info('%s (iso-8859-1).' % self.filename)
        except Exception as e:
            logger.error(u'%s' % e)
        if _content is not None:
            for tag in ['body', 'p', 'table']:
                tag1 = '<{} '.format(tag)
                tag2 = '<{}>'.format(tag)
                tag3 = '</{}>'.format(tag)
                _content = _content.replace(tag1.upper(), tag1)
                _content = _content.replace(tag2.upper(), tag2)
                _content = _content.replace(tag3.upper(), tag3)
            h = html.parser.HTMLParser()
            _content = h.unescape(_content)

        return _content or ''

    @property
    def header(self):
        _header = None
        if '<table' in self.content:
            temp = self.content[self.content.find('<table'):]
            if '</table>' in temp:
                temp = temp[:temp.find('</table>')+len('</table>')]
                _header = temp.strip()
        if _header is None:
            logger.info('%s no header found.' % self.filename)
        elif 'Editable' in _header and '<!--' in _header and '-->' in _header:
            return _header
        else:
            logger.info('%s: text is not a header template.' % self.filename)

    @property
    def footer(self):
        _footer = None
        if 'script=sci_serial' in self.content:
            p_script = self.content.rfind('script=sci_serial')
            text_begin_to_script = self.content[:p_script]
            if '<p ' in text_begin_to_script:
                p_paragraph = text_begin_to_script.rfind('<p ')
                text_paragraph_to_end = self.content[p_paragraph:]
                if '</body>' in text_paragraph_to_end:
                    _footer = text_paragraph_to_end[
                                :text_paragraph_to_end.find('</body>')]
                    _footer = _footer.strip()
        if _footer is None:
            logger.info('%s no footer found.' % self.filename)
        elif 'Editable' in _footer and '<!--' in _footer and '-->' in _footer:
            return _footer
        else:
            logger.info('%s: text is not a footer template.' % self.filename)

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
        new = self.content
        if self.header:
            new = new.replace(self.header, self.anchor)
        if self.footer:
            new = new.replace(self.footer, '<hr noshade="" size="1"/>')
        return new
