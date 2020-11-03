# -*- coding: utf-8 -*-

"""Evaluate simple JavaScript expressions. Use it with care every keystroke triggers an evaluation."""

import os
import subprocess
from albertv0 import *

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'PHP Eval'
__version__ = '1.0'
__trigger__ = 'php '
__author__ = 'Hammed Oyedele'
__dependencies__ = ['php']

iconPath = os.path.dirname(__file__) + '/php.svg'


def run(exp):
    exp = exp.replace('"', '\\"')
    return subprocess.getoutput(f'php -r "{exp}"')


def handleQuery(query):
    if query.isTriggered:
        item = Item(id=__prettyname__, icon=iconPath,
                    completion=query.rawString)
        stripped = query.string.strip()

        if stripped == '':
            item.text = 'Enter a PHP expression...'
        else:
            item.text = run(f'echo {stripped};')
            item.subtext = run(f'echo gettype({stripped});')
            item.addAction(ClipAction('Copy result to clipboard', item.text))

        return item
