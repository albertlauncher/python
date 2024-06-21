# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider


from albert import *
from locale import getdefaultlocale
from socket import timeout
from time import sleep
from urllib import request, parse
import json
from pathlib import Path

md_iid = '2.3'
md_version = "2.0"
md_name = "Wikipedia"
md_description = "Search Wikipedia articles"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/wikipedia"
md_authors = "@manuelschneid3r"


class Plugin(PluginInstance, TriggerQueryHandler):

    baseurl = 'https://en.wikipedia.org/w/api.php'
    searchUrl = 'https://%s.wikipedia.org/wiki/Special:Search/%s'
    user_agent = "org.albert.wikipedia"
    limit = 20
    iconUrls = [f"file:{Path(__file__).parent}/wikipedia.png"]

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(
            self, self.id, self.name, self.description,
            defaultTrigger='wiki ', supportsFuzzyMatching=True
        )
        self.fuzzy = False

        self.local_lang_code = getdefaultlocale()[0]
        if self.local_lang_code:
            self.local_lang_code = self.local_lang_code[0:2]
        else:
            self.local_lang_code = 'en'
            warning("Failed getting language code. Using 'en'.")

        self.fbh = FBH(self)
        self.registerExtension(self.fbh)

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
                if self.local_lang_code in languages:
                    self.baseurl = self.baseurl.replace("en", self.local_lang_code)
        except timeout:
            warning('Error getting languages - socket timed out. Defaulting to EN.')
        except Exception as error:
            warning('Error getting languages (%s). Defaulting to EN.' % error)

    def __del__(self):
        self.deregisterExtension(self.fbh)

    def setFuzzyMatching(self, enabled: bool):
        self.fuzzy = enabled

    def handleTriggerQuery(self, query):
        if stripped := query.string.strip():

            # avoid rate limiting
            for _ in range(50):
                sleep(0.01)
                if not query.isValid:
                    return

            results = []

            params = {
                'action': 'opensearch',
                'search': stripped,
                'limit': self.limit,
                'utf8': 1,
                'format': 'json',
                'profile': 'fuzzy' if self.fuzzy else 'normal'
            }
            get_url = "%s?%s" % (self.baseurl, parse.urlencode(params))
            req = request.Request(get_url, headers={'User-Agent': self.user_agent})

            with request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))

                for i in range(0, min(self.limit, len(data[1]))):
                    title = data[1][i]
                    summary = data[2][i]
                    url = data[3][i]
                    results.append(
                        StandardItem(
                            id=self.id,
                            text=title,
                            subtext=summary if summary else url,
                            iconUrls=self.iconUrls,
                            actions=[
                                Action("open", "Open article on Wikipedia", lambda u=url: openUrl(u)),
                                Action("copy", "Copy URL to clipboard", lambda u=url: setClipboardText(u))
                            ]
                        )
                    )

            if not results:
                results.append(self.createFallbackItem(stripped))

            query.add(results)
        else:
            query.add(
                StandardItem(
                    id=self.id,
                    text=self.name,
                    subtext="Enter a query to search on Wikipedia",
                    iconUrls=self.iconUrls
                )
            )

    def createFallbackItem(self, q: str) -> Item:
        return StandardItem(
            id=self.id,
            text=self.name,
            subtext="Search '%s' on Wikipedia" % q,
            iconUrls=self.iconUrls,
            actions=[
                Action("wiki_search", "Search on Wikipedia",
                       lambda url=self.searchUrl % (self.local_lang_code, q): openUrl(url))
            ]
        )


class FBH(FallbackHandler):

    def __init__(self, p: Plugin):
        FallbackHandler.__init__(self, p.id + 'fb', p.name, p.description)
        self.plugin = p

    def fallbacks(self, q :str):
        return [self.plugin.createFallbackItem(q)]
