# -*- coding: utf-8 -*-

"""Evaluate Mathematica expressions.

Synopsis: <trigger> [expr]"""

#  Copyright (c) 2022 Manuel Schneider

import subprocess
from tempfile import NamedTemporaryFile

from albert import ClipAction, Item, iconLookup

__title__ = 'Mathematica eval'
__version__ = '0.4.0'
__triggers__ = 'mma '
__authors__ = 'Asger Hautop Drewsen'
__exec_deps__ = ['wolframscript']

ICON_PATH = iconLookup('wolfram-mathematica')

def handleQuery(query):
    if not query.isTriggered:
        return

    item = Item(icon=ICON_PATH)
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
