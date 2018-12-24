# -*- coding: utf-8 -*-

"""Fortune wrapper extension"""

from albertv0 import *
from shutil import which
import subprocess as sp

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Fortune"
__version__ = "1.0"
__trigger__ = "fortune"
__author__ = "Kelvin Wong"
__bin__ = "fortune"
__dependencies__ = [__bin__]

if which(__bin__) is None:
    raise Exception("'%s' is not in $PATH." % __bin__)

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
        id=__prettyname__,
        icon=iconPath,
        text=fortune,
        subtext="Copy this random, hopefully interesting, adage",
        completion=query.rawString,
        actions=[ClipAction("Copy to clipboard", fortune)]
    )
