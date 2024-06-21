# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

from albert import *

md_iid = '2.3'
md_version = '2.0'
md_name = 'Zeal'
md_description = 'Search in Zeal docs'
md_license = "MIT"
md_url = 'https://github.com/albertlauncher/python/tree/main/zeal'
md_authors = "@manuelschneid3r"
md_bin_dependencies = ['zeal']


class FBH(FallbackHandler):
    def fallbacks(self, s):
        return [Plugin.createItem(s)] if s else []


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(
            self, self.id, self.name, self.description,
            defaultTrigger='z '
        )
        self.fbh = FBH(
            id=self.id + 'fb',
            name=self.name,
            description=self.description
        )

        self.registerExtension(self.fbh)

    def __del__(self):
        self.deregisterExtension(self.fbh)

    def handleTriggerQuery(self, query):
        if stripped := query.string.strip():
            query.add(self.createItem(stripped))

    @staticmethod
    def createItem(query: str) -> Item:
        return StandardItem(
            id=md_name,
            text=md_name,
            subtext=f"Search '{query}' in Zeal",
            iconUrls=["xdg:zeal"],
            actions=[Action("zeal", "Search in Zeal",
                            lambda q=query: runDetachedProcess(['zeal', q]))]
        )

