# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider


from albert import *
from locale import getdefaultlocale
from socket import timeout
from time import sleep
from urllib import request, parse
import json
from pathlib import Path

md_iid = "3.0"
md_version = "3.0"
md_name = "Wikipedia"
md_description = "Search Wikipedia articles"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/wikipedia"
md_authors = "@manuelschneid3r"

class Plugin(PluginInstance, TriggerQueryHandler):

    wikiurl = "https://en.wikipedia.org/wiki/"
    baseurl = 'https://en.wikipedia.org/w/api.php'
    searchUrl = 'https://%s.wikipedia.org/wiki/Special:Search/%s'
    user_agent = "org.albert.wikipedia"
    limit = 20
    iconUrls = [f"file:{Path(__file__).parent}/wikipedia.png"]


    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

        self.fbh = FBH(self)
        self.fuzzy = False

        self.local_lang_code = getdefaultlocale()[0]
        if self.local_lang_code:
            self.local_lang_code = self.local_lang_code[0:2]
        else:
            self.local_lang_code = 'en'
            warning("Failed getting language code. Using 'en'.")

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
                    Plugin.baseurl = Plugin.baseurl.replace("en", self.local_lang_code)
                    Plugin.wikiurl = Plugin.wikiurl.replace("en", self.local_lang_code)
        except timeout:
            warning('Error getting languages - socket timed out. Defaulting to EN.')
        except Exception as error:
            warning('Error getting languages (%s). Defaulting to EN.' % error)

    def extensions(self):
        return [self, self.fbh]

    def defaultTrigger(self):
        return "wiki "

    def supportsFuzzyMatching(self):
        return True

    def handleTriggerQuery(self, query):
        if stripped := query.string.strip():

            # avoid rate limiting
            for _ in range(50):
                sleep(0.001)
                if not query.isValid:
                    return

            params = {
                'action': 'query',
                'format': 'json',
                'srlimit': 20,
                'formatversion': 2,
                'list': 'search',
                'srsearch': stripped,
                # srinfo = suggestion  could be used for suggestions,
                'srprop': 'snippet|redirecttitle',
            }

            if s := query.state:
                if 'continue' in s:
                    params['sroffset'] = s['continue']['sroffset']
                    params['continue'] = s['continue']['continue']

            get_url = "%s?%s" % (self.baseurl, parse.urlencode(params))
            req = request.Request(get_url, headers={'User-Agent': self.user_agent})
            with request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))

                # store continuation marker if any
                s['continue'] = data.get('continue', None)
                if s['continue']:
                    query.setCanFetchMore()

                results = []
                for d in data['query']['search']:

                    article_title = d['title']
                    article_id = article_title.replace(' ', '_')
                    if 'redirecttitle' in d:
                        article_title = f"{article_title} ({d['redirecttitle']})"
                    article_snippet = d['snippet']

                    results.append(
                        StandardItem(
                            id=article_id,
                            text=article_title,
                            subtext=article_snippet,
                            iconUrls=self.iconUrls,
                            actions=[
                                Action("open", "Open article on Wikipedia",
                                       lambda i=article_id: openUrl(f"{Plugin.wikiurl}{i}")),
                                Action("copy", "Copy URL to clipboard",
                                       lambda i=article_id: setClipboardText(f"{Plugin.wikiurl}{i}"))
                            ]
                        )
                    )

            if not results:
                results.append(self.createFallbackItem(stripped))

            query.add(results)
        else:
            query.add(
                StandardItem(
                    id=self.id(),
                    text=self.name(),
                    subtext="Enter a query to search on Wikipedia",
                    iconUrls=self.iconUrls
                )
            )

    def createFallbackItem(self, q: str) -> Item:
        return StandardItem(
            id=self.id(),
            text=self.name(),
            subtext="Search '%s' on Wikipedia" % q,
            iconUrls=self.iconUrls,
            actions=[
                Action("wiki_search", "Search on Wikipedia",
                       lambda url=self.searchUrl % (self.local_lang_code, q): openUrl(url))
            ]
        )


class FBH(FallbackHandler):

    def __init__(self, p: Plugin):
        FallbackHandler.__init__(self)
        self.plugin = p

    def id(self):
        return "wikipedia.fallbacks"

    def name(self):
        return md_name

    def description(self):
        return md_description

    def fallbacks(self, q :str):
        return [self.plugin.createFallbackItem(q)]
