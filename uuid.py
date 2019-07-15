# -*- coding: utf-8 -*-

"""Generate a uuid and copy to clipboard"""

import uuid

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "UUID Generator"
__version__ = "1.0"
__trigger__ = "uuid"
__author__ = "Josh Crank"
__dependencies__ = []

iconPath = iconLookup('preferences-system-privacy')

def handleQuery(query):
    new_uuid = str(uuid.uuid4())

    if query.isTriggered:
        return  Item(
            id=__prettyname__,
            icon=iconPath,
            text=new_uuid,
            subtext="UUID v4",
            completion=query.rawString,
            actions=[
                ClipAction("Copy to clipboard", new_uuid)
            ]
        )
