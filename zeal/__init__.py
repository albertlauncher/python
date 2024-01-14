# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

from albert import *

md_iid = '2.0'
md_version = '1.2'
md_name = 'Zeal'
md_description = 'Search in Zeal docs'
md_license = "MIT"
md_url = 'https://github.com/albertlauncher/python/zeal'
md_authors = "@manuelschneid3r"
md_bin_dependencies = ['zeal']


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     defaultTrigger='z ')
        PluginInstance.__init__(self, extensions=[self])

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if stripped:
            query.add(
                StandardItem(
                    id=md_name,
                    text=md_name,
                    subtext=f"Search '{stripped}' in Zeal",
                    iconUrls=["xdg:zeal"],
                    actions=[Action("zeal", "Search in Zeal", lambda s=stripped: runDetachedProcess(['zeal', s]))]
                )
            )
