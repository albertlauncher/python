# -*- coding: utf-8 -*-

"""Evaluate simple JavaScript expressions. Use it with care every keystroke triggers an evaluation."""

#  Copyright (c) 2022 Manuel Schneider

import os
import subprocess
from albert import *

__title__ = 'Node Eval'
__version__ = '0.4.0'
__triggers__ = 'node '
__authors__ = 'Hammed Oyedele'
__exec_deps__ = ['node']

iconPath = os.path.dirname(__file__) + '/nodejs.svg'


def run(exp):
    return subprocess.getoutput('node --print "%s"' % exp.replace('"', '\\"'))


def handleQuery(query):
    if query.isTriggered:
        item = Item(
            id=__title__,
            icon=iconPath
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
