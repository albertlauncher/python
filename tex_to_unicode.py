# -*- coding: utf-8 -*-

'''Convert TeX mathmode commands to unicode characters.'''

import re
import unicodedata

from pylatexenc.latex2text import LatexNodes2Text

from albertv0 import *

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'TeX to unicode'
__version__ = '1.0'
__trigger__ = 'tex '
__author__ = 'Asger Hautop Drewsen'
__dependencies__ = ['python-pylatexenc']

COMBINING_LONG_SOLIDUS_OVERLAY = '\u0338'


def handleQuery(query):
    if not query.isTriggered:
        return

    item = Item(completion=query.rawString)
    stripped = query.string.strip()

    success = False
    if stripped:
        if not stripped.startswith('\\'):
            stripped = '\\' + stripped

        # Remove double backslashes (newlines)
        stripped = stripped.replace('\\\\', ' ')

        # pylatexenc doesn't support \not
        stripped = stripped.replace('\\not', '@NOT@')

        # pylatexenc doesn't like backslashes at end of string
        if not stripped.endswith('\\'):
            n = LatexNodes2Text()
            result = n.latex_to_text(stripped)
            if result:
                result = unicodedata.normalize('NFC', result)
                result = re.sub(r'@NOT@\s*(\S)', '\\1' + COMBINING_LONG_SOLIDUS_OVERLAY, result)
                result = result.replace('@NOT@', '')
                result = unicodedata.normalize('NFC', result)
                item.text = result
                item.subtext = 'Result'
                success = True

    if not success:
        item.text = stripped
        item.subtext = 'Type some TeX math'
        success = False

    if success:
        item.addAction(ClipAction('Copy result to clipboard', result))

    return item
