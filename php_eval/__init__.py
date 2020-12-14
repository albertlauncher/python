# -*- coding: utf-8 -*-

"""Evaluate simple PHP expressions. Use it with care every keystroke triggers an evaluation."""

import os
import subprocess
from albert import *
from shutil import which

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'PHP Eval'
__version__ = '1.0'
__trigger__ = 'php '
__author__ = 'Hammed Oyedele'
__dependencies__ = ['php']

iconPath = os.path.dirname(__file__) + '/php.svg'

if which('php') is None:
    raise Exception('"php" is not in $PATH.')


def run(exp):
    return subprocess.getoutput('php -r "%s"' % exp.replace('"', '\\"'))


def handleQuery(query):
    if query.isTriggered:
        item = Item(
            id=__prettyname__,
            icon=iconPath,
            completion=query.rawString,
        )
        stripped = query.string.strip()

        if stripped == '':
            item.text = 'Enter a PHP expression...'
        else:
            item.text = run('echo %s;' % stripped)
            item.subtext = run('echo gettype(%s);' % stripped)
            item.addAction(ClipAction('Copy result to clipboard', item.text))

        return item
