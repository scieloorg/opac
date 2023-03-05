# coding=utf-8

import logging
import os

from bs4 import BeautifulSoup, Comment, element

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "DEBUG")
logging.basicConfig(level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)
fh = logging.FileHandler("journal_pages.log", mode="w")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


PAGE_NAMES = [
    "iaboutj.htm",
    "iedboard.htm",
    "iinstruc.htm",
    "paboutj.htm",
    "pedboard.htm",
    "pinstruc.htm",
    "eaboutj.htm",
    "eedboard.htm",
    "einstruc.htm",
]

PAGE_NAMES_BY_LANG = {
    "en": ["iaboutj.htm", "iedboard.htm", "iinstruc.htm"],
    "pt_BR": ["paboutj.htm", "pedboard.htm", "pinstruc.htm"],
    "es": ["eaboutj.htm", "eedboard.htm", "einstruc.htm"],
}


class OldJournalPageFile(object):
    """
    Representa o arquivo HTML da página secundária do site antigo
    ('iaboutj.htm', 'iedboard.htm', 'iinstruc.htm')
    Sua principal função é retornar o corpo do texto principal,
    excluindo cabeçalho e rodapé, pois só fazem sentido no site antigo
    """

    # about, editors, instructions, contact
    # 'iaboutj.htm', 'iedboard.htm', 'iinstruc.htm'
    anchors = {
        "about": "aboutj",
        "editors": "edboard",
        "instructions": "instruc",
    }
    versions = {"p": "português", "e": "español", "i": "English"}
    h1 = {
        "paboutj.htm": "Sobre o periódico",
        "pedboard.htm": "Corpo Editorial",
        "pinstruc.htm": "Instruções aos autores",
        "eaboutj.htm": "Acerca de la revista",
        "eedboard.htm": "Cuerpo Editorial",
        "einstruc.htm": "Instrucciones a los autores",
        "iaboutj.htm": "About the journal",
        "iedboard.htm": "Editorial Board",
        "iinstruc.htm": "Instructions to authors",
    }

    PT_UNAVAILABLE_MSG = (
        "Informação não disponível em português. " + "Consultar outra versão. "
    )
    ES_UNAVAILABLE_MSG = (
        "Información no disponible en español. " + "Consultar otra versión. "
    )
    EN_UNAVAILABLE_MSG = (
        "Information is not available in English. " + "Consult other version. "
    )

    def __init__(self, filename):
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
        for parser in ["lxml", "html.parser"]:
            if parser is not None:
                self.tree = BeautifulSoup(self.file_content, parser)
            if self.middle_end_insertion_position is None:
                self._info("Not found: end. FAILED {}".format(parser))
            elif self.middle_begin_insertion_position is None:
                self._info("Not found: begin. FAILED {}".format(parser))
            else:
                break

    @property
    def anchor_title(self):
        title = self.h1.get(self.name)
        if title is None:
            alt = [v for k, v in self.h1.items() if self.name[:5] == k[:5]]
            if len(alt) == 1:
                title = alt[0]
        return "<h1>{}</h1>".format(title or "")

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
        logger.debug("%s %s" % (self.filename, msg))

    def _read(self):
        _content = None
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                _content = f.read()
        except UnicodeError:
            with open(self.filename, "r", encoding="iso-8859-1") as f:
                _content = f.read()
                self._info("iso-8859-1")
        except Exception as e:
            self._info("%s" % e)
            logging.error("%s" % e)
        return _content or ""

    def _remove_anchors(self):
        items = self._body_tree.find_all("a")
        for item in items:
            name = item.get("name")
            if name is not None:
                if item.string:
                    item.insert_after(item.string)
                item.extract()

    def _insert_bold_to_p_subtitulo(self):
        p_items = self._body_tree.find_all("p")
        for p in p_items:
            style = p.get("class")
            if style is not None:
                if "subtitulo" in list(style):
                    if not p.find_all("b"):
                        del p["class"]
                        for item in p.children:
                            new_tag = self.tree.new_tag("b")
                            wrap(item, new_tag)

    def find_p_middle_begin(self):
        """
        Localiza no texto <p id="middle_begin"/> que é a posição que indica
        início do bloco de texto principal
        """
        items = [
            p
            for p in self._body_tree.find_all("p")
            if p.get("id", "") == "middle_begin"
        ]
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
            new_tag["id"] = "middle_begin"
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
        table = self._body_tree.find("table")
        if table is not None:
            header = str(table)
            if has_header(header):
                return table

    def find_p_middle_end(self):
        """
        Localiza no texto <p id="middle_end"/> que é a posição que indica
        fim do bloco de texto principal
        """
        items = [
            p for p in self._body_tree.find_all("p") if p.get("id", "") == "middle_end"
        ]
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
            new_tag["id"] = "middle_end"
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
        a_items = self._body_tree.find_all("a")
        for a in a_items:
            href = a.get("href")
            if href is not None:
                href = str(href).strip()
                href_items.append((a, href, a.text))
                if has_footer(href, a):
                    p = a.parent
                    break
        if p is None:
            for hr in self._body_tree.find_all("hr"):
                p = hr
            if p is not None:
                self._info("footer hr")
        if p is not None:
            return p

    def _get_middle_children_eval_child(self, child, task):
        if task == "find_p_begin":
            if child == self.p_middle_begin:
                task = "find_p_end"
            return task, None
        if task == "find_p_end" and child == self.p_middle_end:
            return "stop", None
        if isinstance(child, Comment):
            return task, None
        return task, child

    def _get_middle_children(self):
        task = "find_p_begin"
        items = []
        for child in self._body_tree.children:
            task, item = self._get_middle_children_eval_child(child, task)
            if item is not None:
                items.append(item)
            elif task == "stop":
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
        return ""

    def _check_unavailable_message(self, content):
        if self.version == "português" and "não disponível" in content:
            return self.PT_UNAVAILABLE_MSG
        elif self.version == "español" and "no disponible" in content:
            return self.ES_UNAVAILABLE_MSG
        elif self.version == "English" and "not available" in content:
            return self.EN_UNAVAILABLE_MSG

    def _get_unavailable_message(self):
        self._unavailable_message = None
        text = self._check_unavailable_message(self.body_content)
        if text:
            p_items = self.sorted_by_relevance
            if len((p_items[0][1])) < 300:
                msg = self._check_unavailable_message(p_items[0][1])
                if msg is not None:
                    self._unavailable_message = "<p>{}</p>".format(msg)

    @property
    def sorted_by_relevance(self):
        return sorted([(len(p), p) for p in self.middle_items], reverse=True)

    @property
    def middle_children(self):
        if not hasattr(self, "_middle_children"):
            self._middle_children = self._get_middle_children()
        return self._middle_children

    @property
    def middle_items(self):
        if not hasattr(self, "_middle_items"):
            self._middle_items = [
                child_tostring(item).strip() for item in self.middle_children
            ]
        return self._middle_items

    @property
    def middle_text(self):
        if not hasattr(self, "_middle_text"):
            self._middle_text = "".join([str(item) for item in self.middle_children])
        return self._middle_text

    @property
    def unavailable_message(self):
        self._get_unavailable_message()
        return self._unavailable_message

    def get_alternative_middle_text(self):
        _middle = self.file_content
        for tag_name in ["table", "p", "body"]:
            for tag in [
                "<" + tag_name + " ",
                "<" + tag_name + ">",
                "</" + tag_name + ">",
            ]:
                _middle = _middle.replace(tag.upper(), tag.lower())
        middle = _middle
        if "</table>" in middle:
            middle = middle[middle.find("</table>") + len("</table>") :]
        if "Home" in middle:
            middle = middle[: middle.rfind("Home")]
            middle = middle[: middle.rfind("<p")]
        elif "Volver" in middle:
            middle = middle[: middle.rfind("Volver")]
            middle = middle[: middle.rfind("<p")]
        elif "Voltar" in middle:
            middle = middle[: middle.rfind("Voltar")]
            middle = middle[: middle.rfind("<p")]
        elif '<p class="rodape">' in middle:
            middle = middle[: middle.rfind('<p class="rodape">')]
        elif "://creativecommons.org" in middle:
            middle = middle[: middle.rfind("://creativecommons.org")]
            middle = middle[: middle.rfind("<p")]
        if "</body>" in middle:
            middle = middle[: middle.rfind("</body>")]
        middle = middle.strip()
        self._info("BEGIN:")
        self._info(middle[:100])
        self._info("END:")
        self._info(middle[-100:])
        self._info("REMOVED BEGIN:")
        self._info(_middle[: _middle.find(middle)])
        self._info("REMOVED END:")
        self._info(_middle[_middle.find(middle) + len(middle) :])

        return middle

    def remove_p_in_li(self):
        for li in self._body_tree.find_all("li"):
            p = li.find("p")
            if p is not None:
                p.unwrap()

    @property
    def middle(self):
        self.remove_p_in_li()
        self._remove_anchors()
        self._insert_bold_to_p_subtitulo()
        if self.p_middle_end is None:
            return self.get_alternative_middle_text()
        return self.middle_text

    @property
    def body(self):
        return (
            "<!-- inicio {} -->".format(self.filename)
            + self.anchor
            + self.anchor_title
            + self.middle
            + '<hr noshade="" size="1"/>'
            + "<!-- fim {} -->".format(self.filename)
        )


def has_header(content):
    return (
        "Editable" in content
        and "<!--" in content
        and "-->" in content
        or 'href="#0' in content
        or "script=sci_serial" in content
        or "/scielo.php?lng=" in content
    )


def has_footer(href, a=None):
    if a is not None:
        return (
            "#" == href
            and a.text.strip() == "Home"
            or "script=sci_serial" in href
            and a.text.strip() == "Home"
            or "script=sci_serial" in href
            and a.text.strip() == "Voltar"
            or "script=sci_serial" in href
            and a.text.strip() == "Volver"
            or "javascript:history.back()" == href
        )
    return (
        "script=sci_serial" in href
        and "Home" in href
        or "script=sci_serial" in href
        and "Voltar" in href
        or "script=sci_serial" in href
        and "Volver" in href
        or "javascript:history.back()" in href
    )


def remove_exceding_space_chars(content):
    parts = content.split()
    return " ".join([p for p in parts if len(p) > 0])


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
