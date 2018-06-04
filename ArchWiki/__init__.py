# -*- coding: utf-8 -*-

"""Search Arch Linux Wiki articles."""

from albertv0 import *
from urllib import request, parse
import json
import os

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Arch Wiki"
__version__ = "1.0"
__trigger__ = "awiki "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = "%s/%s.svg" % (os.path.dirname(__file__), __name__)
baseurl = 'https://wiki.archlinux.org/api.php'
user_agent = "org.albert.extension.python.archwiki"


def handleQuery(query):
    if query.isTriggered:

        stripped = query.string.strip()

        if stripped:
            results = []

            params = {
                'action': 'opensearch',
                'search': stripped,
                'limit': "max",
                'redirects': 'resolve',
                'utf8': 1,
                'format': 'json'
            }
            get_url = "%s?%s" % (baseurl, parse.urlencode(params))
            req = request.Request(get_url, headers={'User-Agent': user_agent})

            with request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                for i in range(0, len(data[1])):
                    title = data[1][i]
                    summary = data[2][i]
                    url = data[3][i]

                    results.append(Item(id=__prettyname__,
                                        icon=iconPath,
                                        text=title,
                                        subtext=summary if summary else url,
                                        completion=title,
                                        actions=[
                                            UrlAction("Open article", url),
                                            ClipAction("Copy URL", url)
                                        ]))
            if results:
                return results

            return Item(id=__prettyname__,
                        icon=iconPath,
                        text="Search '%s'" % query.string,
                        subtext="No results. Start a online search on Arch Wiki",
                        completion=query.rawString,
                        actions=[UrlAction("Open search", "https://wiki.archlinux.org/index.php?search=%s" % query.string)])

        else:
            return Item(id=__prettyname__,
                        icon=iconPath,
                        text=__prettyname__,
                        subtext="Enter a query to search on the Arch Wiki",
                        completion=query.rawString)
