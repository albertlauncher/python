# -*- coding: utf-8 -*-

"""
Find relevant Kaomoji's using machine learning.
"""

from albertv0 import *
import os
import json
import urllib.error
from urllib.request import urlopen, Request
from urllib.parse import urlencode

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Dango Kaomoji"
__version__ = "1.0"
__trigger__ = "kao "
__author__ = "David Britt"
__dependencies__ = []

icon_path = os.path.dirname(__file__) + "/kaoicon.svg"
dangoUrl = "https://customer.getdango.com/dango/api/query/kaomoji"


def handleQuery(query):
    results = []

    if query.isTriggered:

        item = Item(
            id=__prettyname__,
            icon=icon_path,
            completion=query.rawString,
            text=__prettyname__,
            actions=[]
        )

        if len(query.string) >= 2:
            try:
                url = "%s?%s" % (dangoUrl, urlencode({"q": query.string}))
                with urlopen(Request(url)) as response:
                    json_data = json.loads(response.read().decode())
                    for emoj in json_data["items"]:
                        results.append(Item(
                            id=__prettyname__,
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
