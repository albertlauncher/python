# -*- coding: utf-8 -*-

"""Search in Gnome dictionary. Needs 'gnome-dictionary' to be already installed. \
Uses similar keyword to Google's dictionary feature: 'def'. \
To search, type 'def <query>'"""

from shutil import which
from subprocess import run

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Gnome Dictionary"
__version__ = "1.0"
__trigger__ = "def "
__author__ = "Nikhil Wanpal"
__dependencies__ = ["gnome-dictionary"]

if which("gnome-dictionary") is None:
    raise Exception("'gnome-dictionary' is not in $PATH.")

iconPath = iconLookup('accessories-dictionary')


def handleQuery(query):
    if query.isTriggered:
        return Item(id=__prettyname__,
                    icon=iconPath,
                    text=__prettyname__,
                    subtext="Search for '%s' using %s" % (query.string, __prettyname__),
                    completion=query.rawString,
                    actions=[ProcAction("Opens %s and searches for '%s'" % (__prettyname__, query.string),
                                        ["gnome-dictionary", "--look-up=%s" % query.string])])
