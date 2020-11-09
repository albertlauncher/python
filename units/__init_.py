# -*- coding: utf-8 -*-

"""Convert units.

This extension is a wrapper for the (extremely) powerful GNU units tool. Note that spaces are \
interpreted as separators, i.e. dont use spaces between numbers and units.

Synopsis:
    <trigger> <src> [dst]
    <src> to <dst>"""

import re
import subprocess as sp
from shutil import which

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "GNU Units"
__version__ = "1.1"
__trigger__ = "units "
__author__ = "Manuel Schneider"
__dependencies__ = ["units"]

if which("units") is None:
    raise Exception("'units' is not in $PATH.")

icon = iconLookup('calc')
if not icon:
    icon = ":python_module"

regex = re.compile(r"(\S+)(?:\s+to)\s+(\S+)")

def stripPrefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def handleQuery(query):

    if query.isTriggered:
        args = query.string.split()
        item = Item(id='python.gnu_units', icon=icon, completion=query.rawString)
        if args:
            try:
                output = sp.check_output(['units', '--strict', '--one-line', '--quiet'] + query.string.split(), stderr=sp.STDOUT).decode()
                item.text = stripPrefix(stripPrefix(output.strip(), "Definition: "), "* ")
                item.addAction(ClipAction("Copy to clipboard", item.text))
            except sp.CalledProcessError as e:
                item.text = e.stdout.decode().strip().partition('\n')[0]
            item.subtext = "Result of 'units %s'" % query.string
        else:
            item.text = "Empty input"
            item.subtext = "Enter something to convert"
        return item

    else:
        match = regex.fullmatch(query.string.strip())
        if match:
            args = match.group(1, 2)
            try:
                item = Item(id='python.gnu_units', icon=icon, completion=query.rawString)
                item.text = sp.check_output(['units', '-t'] + list(args)).decode().strip()
                item.subtext = "Result of 'units -t %s %s'" % args
                item.addAction(ClipAction("Copy to clipboard", item.text))
                return item
            except sp.CalledProcessError as e:
                pass
