# -*- coding: utf-8 -*-

"""This is extension lets your run zeal with a query using albert."""

from albertv0 import *
import subprocess
from shutil import which

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "GNU Units"
__version__ = "1.0"
__trigger__ = "units "
__author__ = "Manuel Schneider"
__dependencies__ = ["units"]


if which("units") is None:
    raise Exception("'units' is not in $PATH.")


icon = iconLookup('calc')
if not icon:
    icon = ":python_module"


def handleQuery(query):
    if query.isTriggered:
        args = query.string.split()
        item = Item(id='python.gnu_units', icon=icon, completion=query.rawString)
        if len(args) < 1:
            item.text = 'Enter something to convert'
            item.subtext = 'Units takes one or two arguments.'
        elif len(args) > 2:
            item.text = 'Too many arguments'
            item.subtext = 'Units takes one or two arguments.'
        else:
            try:
                item.text = subprocess.check_output(['units', '-t'] + args, stderr=subprocess.STDOUT).decode('utf-8').strip()
            except subprocess.CalledProcessError as e:
                item.text = e.stdout.decode('utf-8').strip().partition('\n')[0]
            item.subtext = "Result of 'units -t %s'" % query.string
            item.addAction(Action("Copy to clipboard", lambda: setClipboard(item.text)))
        return [item]
