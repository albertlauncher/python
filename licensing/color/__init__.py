# -*- coding: utf-8 -*-

"""
Displays a color parsed from name, which may be in one of these formats:

* #RGB (each of R, G, and B is a single hex digit)
* #RRGGBB
* #AARRGGBB
* #RRRGGGBBB
* #RRRRGGGGBBBB
* A name from the list of colors defined in the list of SVG color keyword
names provided by the World Wide Web Consortium; for example, "steelblue"
or "gainsboro".

Note: This extension started as a prototype to test the internal color pixmap
generator. However it may serve as a starting point for people having a real
need for color workflows. PR's welcome.
"""

from albert import *
from urllib.parse import quote_plus
from string import hexdigits

md_iid = '2.0'
md_version = '1.0'
md_name = 'Color'
md_description = 'Display color for color codes'
md_license = 'MIT'
md_url = 'https://github.com/albertlauncher/python/color'


class Plugin(PluginInstance, GlobalQueryHandler):

    def __init__(self):
        GlobalQueryHandler.__init__(self,
                                    id=md_id,
                                    name=md_name,
                                    description=md_description,
                                    defaultTrigger='#')
        PluginInstance.__init__(self, extensions=[self])

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
                            id=md_id,
                            text=s,
                            subtext="The color for this code.",
                            iconUrls=[f"gen:?background=%23{s}"],
                        ),
                        1
                    )
                )

        return rank_items
