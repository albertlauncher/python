# -*- coding: utf-8 -*-

"""Open and search in Zeal offline docs.

 Synopsis: <trigger> <query>"""

#  Copyright (c) 2022 Manuel Schneider

from subprocess import run
from albert import *

__title__ = "Zeal"
__version__ = "0.4.0"
__triggers__ = "zl "
__authors__ = "Manuel S."
__exec_deps__ = ["zeal"]

iconPath = iconLookup('zeal')

def handleQuery(query):
    if query.isTriggered:
        return Item(
            id=__title__,
            icon=iconPath,
            text=__title__,
            subtext="Look up %s" % __title__,
            actions=[ProcAction("Start query in %s" % __title__,
                                ["zeal", query.string])]
        )
