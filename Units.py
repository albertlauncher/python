# -*- coding: utf-8 -*-

"""This extension is a wrapper for the (extremely) powerful GNU units tool. \
Note that spaces are separators.

Synopsis: units <input>
Synopsis: <from> to <to>

Examples:

mach to km/hr
0.7day to hour;min
barrel to decimeter^3;inch^3
"""

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

def handleQuery(query):

    if query.isTriggered:
        args = query.string.split()
        item = Item(id='python.gnu_units', icon=icon, completion=query.rawString)
        if args:
            try:
                item.text = sp.check_output(['units', '-t'] + query.string.split(), stderr=sp.STDOUT).decode().strip()
                item.addAction(ClipAction("Copy to clipboard", item.text))
            except sp.CalledProcessError as e:
                item.text = e.stdout.decode().strip().partition('\n')[0]
            item.subtext = "Result of 'units -t %s'" % query.string
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
