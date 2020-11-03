# -*- coding: utf-8 -*-

"""Evaluate simple JavaScript expressions. Use it with care every keystroke triggers an evaluation."""

import os
import subprocess
from albertv0 import *

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'Node Eval'
__version__ = '1.0'
__trigger__ = 'node '
__author__ = 'Hammed Oyedele'
__dependencies__ = ['node']


iconPath = os.path.dirname(__file__) + '/nodejs.svg'


def run(exp):
    exp = exp.replace('"', '\\"')
    return subprocess.getoutput(f'node --print "{exp}"')


def handleQuery(query):
    if query.isTriggered:
        item = Item(id=__prettyname__, icon=iconPath, completion=query.rawString)
        stripped = query.string.strip()

        if stripped == '':
            item.text = 'Enter a JavaScript expression...'
        else:
            item.text = run(stripped)
            item.subtext = run(f'Object.prototype.toString.call({stripped}).slice(8, -1).toLowerCase()')
            item.addAction(ClipAction('Copy result to clipboard', item.text))

        return item
