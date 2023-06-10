# -*- coding: utf-8 -*-
#  Copyright (c) 2022-2023 Manuel Schneider

from albert import *
from time import sleep
from urllib import request, parse
import json
import os

md_iid = '1.0'
md_version = "1.3"
md_name = "ArchLinux Wiki"
md_description = "Search ArchLinux Wiki articles"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/awiki"
md_maintainers = "@manuelschneid3r"


class Plugin(TriggerQueryHandler):

    icon = [os.path.dirname(__file__) + "/ArchWiki.svg"]
    baseurl = 'https://wiki.archlinux.org/api.php'
    search_url = "https://wiki.archlinux.org/index.php?search=%s"
    user_agent = "org.albert.extension.python.archwiki"

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "awiki "

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if stripped:

            # avoid rate limiting
            for number in range(50):
                sleep(0.01)
                if not query.isValid:
                    return;

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

                    results.append(Item(id=md_id,
                                        text=title,
                                        subtext=summary if summary else url,
                                        icon=self.icon,
                                        actions=[
                                            Action("open", "Open article", lambda u=url: openUrl(u)),
                                            Action("copy", "Copy URL", lambda u=url: setClipboardText(u))
                                        ]))
            if results:
                query.add(results)
            else:
                query.add(Item(id=md_id,
                               text="Search '%s'" % query.string,
                               subtext="No results. Start online search on Arch Wiki",
                               icon=self.icon,
                               actions=[Action("search", "Open search", lambda s=query.string: self.search_url % s)]))

        else:
            query.add(Item(id=md_id,
                           text=md_name,
                           icon=self.icon,
                           subtext="Enter a query to search on the Arch Wiki"))
