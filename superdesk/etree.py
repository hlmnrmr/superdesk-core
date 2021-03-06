
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2017 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from lxml import etree  # noqa
from lxml.etree import ParseError  # noqa

# from https://developer.mozilla.org/en-US/docs/Web/HTML/Block-level_elements
BLOCK_ELEMENTS = (
    "address",
    "article",
    "aside",
    "blockquote",
    "br",
    "canvas",
    "dd",
    "div",
    "dl",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hgroup",
    "hr",
    "li",
    "main",
    "nav",
    "noscript",
    "ol",
    "output",
    "p",
    "pre",
    "section",
    "table",
    "tfoot",
    "ul",
    "video")

# from https://www.w3.org/TR/html/syntax.html#void-elements
VOID_ELEMENTS = (
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "keygen",
    "link",
    "menuitem",
    "meta",
    "param",
    "source",
    "track",
    "wbr")


def fix_html_void_elements(element):
    """Use self-closing elements for HTML void elements, and start/end pairs otherwise

    :param element: Element to fix
    :type element: lxml.etree.Element
    :return: fixed Element
    """
    # we want self closing for HTML void elemends and start/end tags otherwise
    # so we set element.text to None for void ones, and empty string otherwise
    for e in element.xpath("//*[not(node())]"):
        e.text = None if e.tag in VOID_ELEMENTS else ''
    return element


def parse_html(html, content='xml', lf_on_block=False, space_on_elements=False):
    """Parse element and return etreeElement

    <div> element is added around the HTML
    recovery is used in case of bad markup
    :param str html: HTML markup
    :param str content: use 'xml' for XHTML or non html XML, and 'html' for HTML or if you are unsure
    :param bool lf_on_block: if True, add a line feed on block elements' tail
    :param bool space_on_elements: if True, add a space on each element's tail
        mainly used to count words with non HTML markup
    :return etree.Element: parsed element
    """
    if not isinstance(html, str):
        raise ValueError("a string is expected")
    if not html:
        return etree.Element('div')

    if content == 'xml':
        # to preserve 'carriage return' otherwise it gets stripped.
        html = html.replace('\r', '&#13;')
        parser = etree.XMLParser(recover=True, remove_blank_text=True)
        root = etree.fromstring("<div>" + html + "</div>", parser)
    elif content == 'html':
        parser = etree.HTMLParser(recover=True, remove_blank_text=True)
        root = etree.fromstring(html, parser)
        if root is None:
            root = etree.Element('div')
        else:
            root = root.find('body')
            root.tag = 'div'
    else:
        raise ValueError('invalid content: {}'.format(content))
    if lf_on_block:
        for elem in root.iterfind('.//'):
            if elem.tag in BLOCK_ELEMENTS:
                elem.tail = (elem.tail or '') + '\n'
    if space_on_elements:
        for elem in root.iterfind('.//'):
            elem.tail = (elem.tail or '') + ' '
    return root


def to_string(elem, encoding="unicode", method="xml", remove_root_div=True):
    """Convert Element to string

    :param etree.Element elem: element to convert
    :param str encoding: encoding to use (same as for etree.tostring)
    :param str method: method to use (same as for etree.tostring)
    :param bool remove_root_dir: if True remove surrounding <div> which is added by parse_html
    :return str: converted element
    """
    string = etree.tostring(elem, encoding=encoding, method=method)
    if remove_root_div:
        if encoding == "unicode":
            div_start = "<div>"
            div_end = "</div>"
        else:
            div_start = b"<div>"
            div_end = b"</div>"
        if string.startswith(div_start) and string.endswith(div_end):
            return string[len(div_start):-len(div_end)]
    return string
