# -*- coding: utf-8 -*-

"""This is a simple trash extension providing a single item which opens the systems virtual trash \
location in your default file manager on activation."""

import re

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Trash"
__version__ = "1.0"
__trigger__ = "trash "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = iconLookup("user-trash-full")


def handleQuery(query):

    if query.string.strip() and "trash".startswith(query.string.lower()):
        pattern = re.compile(query.string, re.IGNORECASE)
        return Item(
            id="trash-open",
            icon=iconPath,
            text=pattern.sub(lambda m: "<u>%s</u>" % m.group(0), "Trash"),
            subtext="Show trash folder",
            completion="trash",
            actions=[UrlAction("Show", "trash:///")]
        )
