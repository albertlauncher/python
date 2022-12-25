# -*- coding: utf-8 -*-

"""Fire up an external search in GoldenDict.

Synopsis: <trigger> <query>"""

#  Copyright (c) 2022 Manuel Schneider

from subprocess import run
from albert import Item, ProcAction, iconLookup

__title__ = "GoldenDict"
__version__ = "0.4.0"
__triggers__ = "gd "
__authors__ = "Manuel S."
__exec_deps__ = ["goldendict"]

iconPath = iconLookup('goldendict')


def handleQuery(query):
    if query.isTriggered:
        return Item(id=__title__,
                    icon=iconPath,
                    text=__title__,
                    subtext="Look up '%s' using %s" % (query.string, __title__),
                    actions=[ProcAction("Start query in %s" % __title__,
                                        ["goldendict", query.string])])
