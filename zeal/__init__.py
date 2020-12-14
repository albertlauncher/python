# -*- coding: utf-8 -*-

"""Open and search in Zeal offline docs.

 Synopsis: <trigger> <query>"""

from shutil import which
from subprocess import run

from albert import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Zeal"
__version__ = "1.0"
__trigger__ = "zl "
__author__ = "Manuel Schneider"
__dependencies__ = ["zeal"]

if which("zeal") is None:
    raise Exception("'zeal' is not in $PATH.")

iconPath = iconLookup('zeal')


def handleQuery(query):
    if query.isTriggered:
        return Item(
            id=__prettyname__,
            icon=iconPath,
            text=__prettyname__,
            subtext="Look up %s" % __prettyname__,
            completion=query.rawString,
            actions=[ProcAction("Start query in %s" % __prettyname__,
                                ["zeal", query.string])]
        )
