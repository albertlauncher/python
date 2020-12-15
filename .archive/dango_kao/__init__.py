# -*- coding: utf-8 -*-

"""Find kaomojis using getdango.com

Dango uses a form of artificial intelligence called deep learning to understand the nuances of \
human emotion, and predict emoji based on what you type.

Synopsis: <trigger> <query>"""

from albert import *
import os
import json
import urllib.error
from urllib.request import urlopen, Request
from urllib.parse import urlencode

__title__ = "Dango Kaomoji"
__version__ = "0.4.0"
__triggers__ = "kao "
__authors__ = "David Britt"

icon_path = os.path.dirname(__file__) + "/kaoicon.svg"
dangoUrl = "https://customer.getdango.com/dango/api/query/kaomoji"


def handleQuery(query):
    results = []

    if query.isTriggered:

        item = Item(
            id=__title__,
            icon=icon_path,
            text=__title__,
        )

        if len(query.string) >= 2:
            try:
                url = "%s?%s" % (dangoUrl, urlencode({"q": query.string}))
                with urlopen(Request(url)) as response:
                    json_data = json.loads(response.read().decode())
                    for emoj in json_data["items"]:
                        results.append(Item(
                            id=__title__,
                            icon=icon_path,
                            text=emoj["text"],
                            actions=[
                                ClipAction(
                                    "Copy translation to clipboard", emoj["text"])
                            ]
                        ))
            except urllib.error.URLError as urlerr:
                print("Troubleshoot internet connection: %s" % urlerr)
                item.subtext = "Connection error"
                return item
        else:
            item.subtext = "Search emojis!"
            return item

    return results
