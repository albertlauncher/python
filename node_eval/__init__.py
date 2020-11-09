# -*- coding: utf-8 -*-

"""Evaluate simple JavaScript expressions. Use it with care every keystroke triggers an evaluation."""

import os
import subprocess
from albertv0 import *
from shutil import which

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'Node Eval'
__version__ = '1.0'
__trigger__ = 'node '
__author__ = 'Hammed Oyedele'
__dependencies__ = ['node']

if which('node') is None:
    raise Exception('"node" is not in $PATH.')

iconPath = os.path.dirname(__file__) + '/nodejs.svg'


def run(exp):
    return subprocess.getoutput('node --print "%s"' % exp.replace('"', '\\"'))


def handleQuery(query):
    if query.isTriggered:
        item = Item(
            id=__prettyname__,
            icon=iconPath,
            completion=query.rawString,
        )
        stripped = query.string.strip()

        if stripped == '':
            item.text = 'Enter a JavaScript expression...'
        else:
            item.text = run(stripped)
            item.subtext = run(
                'Object.prototype.toString.call(%s).slice(8, -1).toLowerCase()' % stripped)
            item.addAction(ClipAction('Copy result to clipboard', item.text))

        return item
