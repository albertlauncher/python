# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

import json
from pathlib import Path
from time import sleep
from urllib import request, parse

from albert import *

md_iid = '2.0'
md_version = "1.5"
md_name = "Arch Linux Wiki"
md_description = "Search Arch Linux Wiki articles"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/master/arch_wiki"
md_authors = "@manuelschneid3r"


class Plugin(PluginInstance, TriggerQueryHandler):

    baseurl = 'https://wiki.archlinux.org/api.php'
    search_url = "https://wiki.archlinux.org/index.php?search=%s"
    user_agent = "org.albert.extension.python.archwiki"

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     defaultTrigger='awiki ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/arch.svg"]

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
                'limit': "max",
                'redirects': 'resolve',
                'utf8': 1,
                'format': 'json'
            }
            get_url = "%s?%s" % (self.baseurl, parse.urlencode(params))
            req = request.Request(get_url, headers={'User-Agent': self.user_agent})

            with request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                for i in range(0, len(data[1])):
                    title = data[1][i]
                    summary = data[2][i]
                    url = data[3][i]

                    results.append(StandardItem(id=md_id,
                                                text=title,
                                                subtext=summary if summary else url,
                                                iconUrls=self.iconUrls,
                                                actions=[
                                                    Action("open", "Open article", lambda u=url: openUrl(u)),
                                                    Action("copy", "Copy URL", lambda u=url: setClipboardText(u))
                                                ]))
            if results:
                query.add(results)
            else:
                query.add(StandardItem(id=md_id,
                                       text="Search '%s'" % query.string,
                                       subtext="No results. Start online search on Arch Wiki",
                                       iconUrls=self.iconUrls,
                                       actions=[Action("search", "Open search",
                                                       lambda s=query.string: openUrl(self.search_url % s))]))

        else:
            query.add(StandardItem(id=md_id,
                                   text=md_name,
                                   iconUrls=self.iconUrls,
                                   subtext="Enter a query to search on the Arch Wiki"))
