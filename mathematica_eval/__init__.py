# -*- coding: utf-8 -*-

"""Evaluate Mathematica expressions.

Synopsis: <trigger> [expr]"""

import subprocess
from shutil import which
from tempfile import NamedTemporaryFile

from albert import ClipAction, Item, iconLookup

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'Mathematica eval'
__version__ = '1.0'
__trigger__ = 'mma '
__author__ = 'Asger Hautop Drewsen'
__dependencies__ = ['mathematica']

if not which('wolframscript'):
    raise Exception("`wolframscript` is not in $PATH.")

ICON_PATH = iconLookup('wolfram-mathematica')

def handleQuery(query):
    if not query.isTriggered:
        return

    item = Item(completion=query.rawString, icon=ICON_PATH)
    stripped = query.string.strip()

    if stripped:
        with NamedTemporaryFile() as f:
            f.write(bytes(stripped, 'utf-8'))
            f.flush()
            output = subprocess.check_output(['wolframscript', '-print', '-f', f.name])
        result = str(output.strip(), 'utf-8')
        item.text = result
        item.subtext = 'Result'
        item.addAction(ClipAction('Copy result to clipboard', result))
    else:
        item.text = ''
        item.subtext = 'Type a Mathematica expression'

    return item
