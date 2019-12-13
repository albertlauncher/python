# -*- coding: utf-8 -*-

"""Search Remmina connections."""

from albertv0 import *
import os

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Remmina"
__version__ = "0.1"
__trigger__ = "rm"
__author__ = "Oğuzcan Küçükbayrak"
__dependencies__ = []

iconPath = "%s/%s.svg" % (os.path.dirname(__file__), __name__)
connectionsPath = '/home/okb/.local/share/remmina'
def handleQuery(query):
    if query.isTriggered:
        return Item(
                    id=__prettyname__,
                    icon=iconPath,
                    text="Remmina",
                    subtext="This is subtext.",
                    completion=query.rawString,
                    actions=[ProcAction("Open Remmina", "remmina")]
                )

