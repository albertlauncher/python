# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

import albert

md_iid = "3.0"
md_version = "3.0"
md_name = "Zeal"
md_description = "Search in Zeal docs"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/zeal"
md_authors = "@manuelschneid3r"
md_bin_dependencies = ['zeal']

def createItem(query: str):
    return albert.StandardItem(
        id=md_name,
        text=md_name,
        subtext=f"Search '{query}' in Zeal",
        iconUrls=["xdg:zeal"],
        actions=[albert.Action("zeal", "Search in Zeal",
                               lambda q=query: albert.runDetachedProcess(['zeal', q]))]
    )

class FBH(albert.FallbackHandler):

    def id(self):
        return "zeal_fbh"

    def name(self):
        return md_name

    def description(self):
        return md_description

    def fallbacks(self, s):
        return [createItem(s)] if s else []


class Plugin(albert.PluginInstance, albert.TriggerQueryHandler):

    def __init__(self):
        albert.PluginInstance.__init__(self)
        albert.TriggerQueryHandler.__init__(self)
        self.fbh = FBH()

    def defaultTrigger(self):
        return "z "

    def extensions(self):
        return [self, self.fbh]

    def handleTriggerQuery(self, query):
        if stripped := query.string.strip():
            query.add(createItem(stripped))
