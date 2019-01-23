# -*- coding: utf-8 -*-

"""Search Wikipedia articles.

Synopsis: <trigger> <filter>"""

from albertv0 import *
from locale import getdefaultlocale
from urllib import request, parse
import json
import time
import os

__iid__ = "PythonInterface/v0.3"
__prettyname__ = "Wikipedia"
__version__ = "1.4"
__trigger__ = "wiki "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = iconLookup('wikipedia')
if not iconPath:
    iconPath = os.path.dirname(__file__)+"/wikipedia.svg"
baseurl = 'https://en.wikipedia.org/w/api.php'
user_agent = "org.albert.extension.python.wikipedia"
limit = 20


def initialize():
    global baseurl
    params = {
        'action': 'query',
        'meta': 'siteinfo',
        'utf8': 1,
        'siprop': 'languages',
        'format': 'json'
    }

    get_url = "%s?%s" % (baseurl, parse.urlencode(params))
    req = request.Request(get_url, headers={'User-Agent': user_agent})
    with request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        languages = [lang['code'] for lang in data['query']['languages']]
        local_lang_code = getdefaultlocale()[0][0:2]
        if local_lang_code in languages:
            baseurl = baseurl.replace("en", local_lang_code)


def handleQuery(query):
    if query.isTriggered:
        query.disableSort()

        # avoid rate limiting
        time.sleep(0.1)
        if not query.isValid:
            return

        stripped = query.string.strip()

        if stripped:
            results = []

            params = {
                'action': 'opensearch',
                'search': stripped,
                'limit': limit,
                'utf8': 1,
                'format': 'json'
            }
            get_url = "%s?%s" % (baseurl, parse.urlencode(params))
            req = request.Request(get_url, headers={'User-Agent': user_agent})

            with request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))

                for i in range(0, min(limit, len(data[1]))):
                    title = data[1][i]
                    summary = data[2][i]
                    url = data[3][i]

                    results.append(Item(id=__prettyname__,
                                        icon=iconPath,
                                        text=title,
                                        subtext=summary if summary else url,
                                        completion=title,
                                        actions=[
                                            UrlAction("Open article on Wikipedia", url),
                                            ClipAction("Copy URL", url)
                                        ]))

            return results
        else:
            return Item(id=__prettyname__,
                        icon=iconPath,
                        text=__prettyname__,
                        subtext="Enter a query to search on Wikipedia",
                        completion=query.rawString)
