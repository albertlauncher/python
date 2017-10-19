# -*- coding: utf-8 -*-

"""Fire up an external search in GoldenDict.
Just type gd <query>"""

from albertv0 import *
from subprocess import run
from shutil import which

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "GoldenDict"
__version__ = "1.0"
__trigger__ = "gd "
__author__ = "Manuel Schneider"
__dependencies__ = ["goldendict"]


if which("goldendict") is None:
    raise Exception("'goldendict' is not in $PATH.")


iconPath = iconLookup('goldendict')


def handleQuery(query):
    if query.isTriggered:
        return [
            Item(
                id=__prettyname__,
                icon=iconPath,
                text=__prettyname__,
                subtext="Look up '%s' using %s" % (query.string, __prettyname__),
                completion=query.rawString,
                actions=[ProcAction("Start query in %s" % __prettyname__,
                                    ["goldendict", query.string])])
        ]
