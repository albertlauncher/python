# -*- coding: utf-8 -*-

"""Gnome dictionary.

Needs 'gnome-dictionary' to be already installed.

Sysnopsis: <trigger> <query>"""

#  Copyright (c) 2022 Manuel Schneider

from subprocess import run

from albert import *

__title__ = "Gnome Dictionary"
__version__ = "0.4.0"
__triggers__ = "def "
__authors__ = "Nikhil Wanpal"
__exec_deps__ = ["gnome-dictionary"]

iconPath = iconLookup('accessories-dictionary')


def handleQuery(query):
    if query.isTriggered:
        return Item(id=__title__,
                    icon=iconPath,
                    text=__title__,
                    subtext="Search for '%s' using %s" % (query.string, __title__),
                    actions=[ProcAction("Opens %s and searches for '%s'" % (__title__, query.string),
                                        ["gnome-dictionary", "--look-up=%s" % query.string])])
