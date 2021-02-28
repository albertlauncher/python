# -*- coding: utf-8 -*-

"""Generate a UUID v4 and copy it to clipboard"""

import uuid

from albert import *

__title__ = "UUID Generator"
__version__ = "0.1.0"
__authors__ = ["Josh Crank", "mkobayashime"]

iconPath = iconLookup('preferences-system-privacy')

def handleQuery(query):
    if query.string.strip() and "uuid".startswith(query.string.lower()):
        new_uuid = str(uuid.uuid4())
        return Item(
            id=__title__,
            icon=iconPath,
            text="UUID v4",
            subtext=new_uuid,
            completion="uuid",
            actions=[
                ClipAction("Copy to clipboard", new_uuid)
            ]
        )

