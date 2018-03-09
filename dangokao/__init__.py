# -*- coding: utf-8 -*-

"""
Find relevant Kaomoji's using machine learning.
"""

from albertv0 import *
import os
import json
import urllib.error
import requests

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
                with requests.get(dangoUrl, params={"q": query.string}) as api_response:
                    json_data = json.loads(api_response.text)
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
