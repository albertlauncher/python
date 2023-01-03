# -*- coding: utf-8 -*-

"""Search Wikipedia articles.

Synopsis: <trigger> <filter>"""

#  Copyright (c) 2022-2023 Manuel Schneider

from albert import *
from locale import getdefaultlocale
from urllib import request, parse
import json
import time
import os
from socket import timeout

md_iid = "0.5"
md_version = "1.5"
md_name = "Wikipedia"
md_description = "Search Wikipedia articles."
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/wikipedia"
md_maintainers = "@manuelschneid3r"


class Plugin(QueryHandler):

    iconPath = ":wikipedia"
    baseurl = 'https://en.wikipedia.org/w/api.php'
    user_agent = "org.albert.wikipedia"
    limit = 20

    def id(self):
        return __name__

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "wiki "


    def initialize(self):
        params = {
            'action': 'query',
            'meta': 'siteinfo',
            'utf8': 1,
            'siprop': 'languages',
            'format': 'json'
        }

        get_url = "%s?%s" % (self.baseurl, parse.urlencode(params))
        req = request.Request(get_url, headers={'User-Agent': self.user_agent})
        try:
            with request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                languages = [lang['code'] for lang in data['query']['languages']]
                local_lang_code = getdefaultlocale()[0][0:2]
                if local_lang_code in languages:
                    self.baseurl = self.baseurl.replace("en", local_lang_code)
        except timeout:
            critical('Error getting languages - socket timed out. Defaulting to EN.')
        except Exception as error:
            critical('Error getting languages (%s). Defaulting to EN.' % error)


    def handleQuery(self, query):
        stripped = query.string.strip()
        if stripped:
            # avoid rate limiting
            time.sleep(0.1)
            if not query.isValid:
                return

            results = []

            params = {
                'action': 'opensearch',
                'search': stripped,
                'limit': self.limit,
                'utf8': 1,
                'format': 'json'
            }
            get_url = "%s?%s" % (self.baseurl, parse.urlencode(params))
            req = request.Request(get_url, headers={'User-Agent': self.user_agent})

            with request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))

                for i in range(0, min(self.limit, len(data[1]))):
                    title = data[1][i]
                    summary = data[2][i]
                    url = data[3][i]

                    results.append(Item(id="wiki",
                                        text=title,
                                        subtext=summary if summary else url,
                                        completion=title,
                                        icon=[self.iconPath],
                                        actions=[
                                            Action("open", "Open article on Wikipedia", lambda u=url: openUrl(u)),
                                            Action("copy", "Copy URL to clipboard", lambda u=url: setClipBoardText(u))
                                        ]))

            query.add(results)
        else:
            query.add(Item(id="wiki",
                           text=md_name,
                           subtext="Enter a query to search on Wikipedia",
                           icon=[self.iconPath]))
