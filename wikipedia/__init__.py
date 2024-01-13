# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider


from albert import *
from locale import getdefaultlocale
from socket import timeout
from time import sleep
from urllib import request, parse
import json
from pathlib import Path

md_iid = '2.0'
md_version = "1.10"
md_name = "Wikipedia"
md_description = "Search Wikipedia articles"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/master/wikipedia"
md_authors = "@manuelschneid3r"


class WikiFallbackHandler(FallbackHandler):
    def __init__(self):
        FallbackHandler.__init__(self,
                                 id=f"{md_id}_fb",
                                 name=f"{md_name} fallback",
                                 description="Wikipedia fallback search")

    def fallbacks(self, query_string):
        stripped = query_string.strip()
        return [Plugin.createFallbackItem(query_string)] if stripped else []


class Plugin(PluginInstance, TriggerQueryHandler):

    baseurl = 'https://en.wikipedia.org/w/api.php'
    searchUrl = 'https://%s.wikipedia.org/wiki/Special:Search/%s'
    user_agent = "org.albert.wikipedia"
    limit = 20
    iconUrls = [f"file:{Path(__file__).parent}/wikipedia.png"]

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     defaultTrigger='wiki ')
        self.wiki_fb = WikiFallbackHandler()
        PluginInstance.__init__(self, extensions=[self, self.wiki_fb])

        params = {
            'action': 'query',
            'meta': 'siteinfo',
            'utf8': 1,
            'siprop': 'languages',
            'format': 'json'
        }

        Plugin.local_lang_code = getdefaultlocale()[0]
        if Plugin.local_lang_code:
            Plugin.local_lang_code = Plugin.local_lang_code[0:2]
        else:
            Plugin.local_lang_code = 'en'
            warning("Failed getting language code. Using 'en'.")

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

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if stripped:
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
                    results.append(
                        StandardItem(
                            id=md_id,
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
                results.append(Plugin.createFallbackItem(stripped))

            query.add(results)
        else:
            query.add(
                StandardItem(
                    id=md_id,
                    text=md_name,
                    subtext="Enter a query to search on Wikipedia",
                    iconUrls=self.iconUrls
                )
            )

    @staticmethod
    def createFallbackItem(query_string):
        return StandardItem(
            id=md_id,
            text=md_name,
            subtext="Search '%s' on Wiki" % query_string,
            iconUrls=Plugin.iconUrls,
            actions=[
                Action("wiki_search", "Search on Wikipedia",
                       lambda url=Plugin.searchUrl % (Plugin.local_lang_code, query_string): openUrl(url))
            ]
        )
