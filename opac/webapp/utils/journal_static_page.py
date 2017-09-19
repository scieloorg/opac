# coding=utf-8


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
