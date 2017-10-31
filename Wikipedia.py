# -*- coding: utf-8 -*-

"""Search Wikipedia articles."""

from albertv0 import *
from locale import getlocale
from urllib import request, parse
import json

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Wikipedia"
__version__ = "1.0"
__trigger__ = "wiki "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = iconLookup('wikipedia')
if not iconPath:
    iconPath = ":python_module"
baseurl = 'https://en.wikipedia.org/w/api.php'
user_agent = "org.arlbert.extension.python.wikipedia"
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
        data = json.load(response)
        languages = [lang['code'] for lang in data['query']['languages']]
        local_lang_code = getlocale()[0][0:2]
        if local_lang_code in languages:
            baseurl = baseurl.replace("en", local_lang_code)


def handleQuery(query):
    if query.isTriggered:

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
            critical(get_url)

            with request.urlopen(req) as response:
                data = json.load(response)
                print(json, flush=True)
                for i in range(0, limit):

                    title = data[1][i]
                    summary = data[2][i]
                    url = data[3][i]

                    item = Item(id=__prettyname__,
                                icon=iconPath,
                                text=title,
                                subtext=summary,
                                completion=title,
                                actions=[UrlAction(text="UrlAction", url=url)])

                    results.append(item)
            return results
        else:
            return [Item(id=__prettyname__,
                         icon=iconPath,
                         text=__prettyname__,
                         subtext="Enter a query to search on Wikipedia",
                         completion=query.rawString)]
