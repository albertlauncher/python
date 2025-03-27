# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

"""
Displays a color parsed from a code, which may be in one of these formats:

* #RGB (each of R, G, and B is a single hex digit)
* #RRGGBB
* #AARRGGBB
* #RRRGGGBBB
* #RRRRGGGGBBBB

Note: This extension started as a prototype to test the internal color pixmap generator. However it may serve as a \
starting point for people having a real need for color workflows. PR's welcome.
"""

from albert import *
from string import hexdigits

md_iid = "3.0"
md_version = "2.0"
md_name = "Color"
md_description = "Display color for color codes"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/color"
md_authors = "@manuelschneid3r"


class Plugin(PluginInstance, GlobalQueryHandler):

    def __init__(self):
        PluginInstance.__init__(self)
        GlobalQueryHandler.__init__(self)

    def defaultTrigger(self):
        return '#'

    def handleGlobalQuery(self, query):
        rank_items = []
        s = query.string.strip()
        if s:
            if s.startswith('#'):  # remove hash
                s = s[1:]

            # check length and hex
            if any([len(s) == l for l in [3, 6, 8, 9, 12]]) and all(c in hexdigits for c in s):
                rank_items.append(
                    RankItem(
                        StandardItem(
                            id=self.id(),
                            text=s,
                            subtext="The color for this code.",
                            iconUrls=[f"gen:?background=%23{s}"],
                        ),
                        1
                    )
                )

        return rank_items

    def configWidget(self):
        return [{ 'type': 'label', 'text': __doc__.strip() }]
    