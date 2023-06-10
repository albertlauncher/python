# -*- coding: utf-8 -*-

"""Evaluate simple PHP expressions. Use it with care every keystroke triggers an evaluation."""

#  Copyright (c) 2022 Manuel Schneider

import os
import subprocess
from albert import *

__title__ = 'PHP Eval'
__version__ = '0.4.0'
__triggers__ = 'php '
__authors__ = 'Hammed Oyedele'
__exec_deps__ = ['php']

iconPath = os.path.dirname(__file__) + '/php.svg'

def run(exp):
    return subprocess.getoutput('php -r "%s"' % exp.replace('"', '\\"'))


def handleQuery(query):
    if query.isTriggered:
        item = Item(
            id=__title__,
            icon=iconPath
        )
        stripped = query.string.strip()

        if stripped == '':
            item.text = 'Enter a PHP expression...'
        else:
            item.text = run('echo %s;' % stripped)
            item.subtext = run('echo gettype(%s);' % stripped)
            item.addAction(ClipAction('Copy result to clipboard', item.text))

        return item
