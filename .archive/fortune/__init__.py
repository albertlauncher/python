# -*- coding: utf-8 -*-

"""Display random poignant, inspirational, silly or snide phrase.

Fortune wrapper extension.

Synopsis: <trigger>"""

#  Copyright (c) 2022 Manuel Schneider

import subprocess as sp
from albert import *

__title__ = "Fortune"
__version__ = "0.4.0"
__triggers__ = "fortune"
__authors__ = "Kelvin Wong"
__exec_deps__ = ["fortune"]

iconPath = iconLookup("font")


def handleQuery(query):
    if query.isTriggered:
        newFortune = generateFortune()
        if newFortune is not None:
            return getFortuneItem(query, newFortune)


def generateFortune():
    try:
        return sp.check_output(["fortune", "-s"]).decode().strip()
    except sp.CalledProcessError as e:
        return None


def getFortuneItem(query, fortune):
    return Item(
        id=__title__,
        icon=iconPath,
        text=fortune,
        subtext="Copy this random, hopefully interesting, adage",
        actions=[ClipAction("Copy to clipboard", fortune)]
    )
