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
__version__ = "1.2"
__trigger__ = "units "
__author__ = "Manuel Schneider, iyzana"
__dependencies__ = ["units"]

if which("units") is None:
    raise Exception("'units' is not in $PATH.")

icon = iconLookup('calc')
if not icon:
    icon = ":python_module"

regex = re.compile(r"(\S+)(?:\s+to)\s+(\S+)")
unitListOutput = re.compile(r"(\d+(e[+-]\d{2,})?;)+[\d.]+(e[+-]\d{2,})?")


def getUnitsResult(args):
    command = ['units', '--terse', '--'] + list(args)
    query = "units -t -- %s" % ' '.join(args)
    try:
        output = sp.check_output(command, stderr=sp.STDOUT).decode().strip()

        # usually we want terse output, but when we get a unit-list output
        # it looks like this 1;124;18;11;14.025322 which is not friendly
        # so we're falling back to not quite terse output
        if unitListOutput.fullmatch(output):
            command = ['units', '--strict', '--one-line',
                       '--quiet', '--'] + list(args)
            query = "units -s1q -- %s" % ' '.join(args)
            output = sp.check_output(
                command, stderr=sp.STDOUT).decode().strip()

        return (output, query, True)
    except sp.CalledProcessError as e:
        return (e.stdout.decode().strip().splitlines()[0], query, False)


def handleQuery(query):
    if query.isTriggered:
        args = query.string.split()
        item = Item(id='python.gnu_units', icon=icon,
                    completion=query.rawString)
        if args:
            result, command, success = getUnitsResult(args)
            item.text = result
            item.subtext = "Result of '%s'" % command
            item.addAction(ClipAction("Copy to clipboard", item.text))
        else:
            item.text = "Empty input"
            item.subtext = "Enter a query of the form <from> [<to>]"
        return item
    else:
        match = regex.fullmatch(query.string.strip())
        if match:
            args = match.group(1, 2)
            result, command, success = getUnitsResult(args)
            if not success:
                return
            item = Item(id='python.gnu_units', icon=icon,
                        completion=query.rawString)
            item.text = result
            item.subtext = "Result of '%s'" % command
            item.addAction(ClipAction("Copy to clipboard", item.text))
            return item
