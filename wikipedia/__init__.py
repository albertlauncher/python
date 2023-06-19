# -*- coding: utf-8 -*-

#  Copyright (c) 2022-2023 Manuel Schneider

from albert import *
from locale import getdefaultlocale
from socket import timeout
from time import sleep
from urllib import request, parse
import json
import os

md_iid = '1.0'
md_version = "1.7"
md_name = "Wikipedia"
md_description = "Search Wikipedia articles."
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/wikipedia"


class Plugin(TriggerQueryHandler):

    iconPath = os.path.dirname(__file__) + "/wikipedia.png"
    baseurl = 'https://en.wikipedia.org/w/api.php'
    searchUrl = 'https://%s.wikipedia.org/wiki/Special:Search/%s'
    user_agent = "org.albert.wikipedia"
    limit = 20

    def id(self):
        return md_id

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

        self.local_lang_code = getdefaultlocale()[0][0:2]

        get_url = "%s?%s" % (self.baseurl, parse.urlencode(params))
        req = request.Request(get_url, headers={'User-Agent': self.user_agent})
        try:
            with request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                languages = [lang['code'] for lang in data['query']['languages']]
                if self.local_lang_code in languages:
                    self.baseurl = self.baseurl.replace("en", self.local_lang_code)
        except timeout:
            critical('Error getting languages - socket timed out. Defaulting to EN.')
        except Exception as error:
            critical('Error getting languages (%s). Defaulting to EN.' % error)

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if stripped:
            # avoid rate limiting
            for number in range(50):
                sleep(0.01)
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

                    results.append(Item(id=md_id,
                                        text=title,
                                        subtext=summary if summary else url,
                                        icon=[self.iconPath],
                                        actions=[
                                            Action("open", "Open article on Wikipedia", lambda u=url: openUrl(u)),
                                            Action("copy", "Copy URL to clipboard", lambda u=url: setClipboardText(u))
                                        ]))
            if not results:
                results.append(self._createFallbackItem(stripped))
            query.add(results)
        else:
            query.add(Item(id=md_id,
                           text=md_name,
                           subtext="Enter a query to search on Wikipedia",
                           icon=[self.iconPath]))

    def _createFallbackItem(self, query_string):
        return Item(
            id=md_id,
            text=md_name,
            subtext="Search '%s' on Wiki" % query_string,
            icon=[self.iconPath],
            actions=[
                Action("wiki_search", "Search on Wikipedia",
                       lambda url=Plugin.searchUrl % (self.local_lang_code, query_string): openUrl(url))
            ]
        )