# -*- coding: utf-8 -*-

"""Open virtual trash location.

This extension provides a single item which opens the systems virtual trash \
location in your default file manager.

Synopsis: <trigger>"""

#  Copyright (c) 2022 Manuel Schneider

import re

from albert import Item, UrlAction, iconLookup

__title__ = "Trash"
__version__ = "0.4.0"
__authors__ = "Manuel S."
iconPath = iconLookup("user-trash-full")

def handleQuery(query):
    if query.string.strip() and "trash".startswith(query.string.lower()):
        pattern = re.compile(query.string, re.IGNORECASE)
        return Item(id="trash-open",
                    icon=iconPath,
                    text=pattern.sub(lambda m: "<u>%s</u>" % m.group(0), "Trash"),
                    subtext="Show trash folder",
                    completion="trash",
                    actions=[UrlAction("Show", "trash:///")])
