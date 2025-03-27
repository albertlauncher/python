# -*- coding: utf-8 -*-
# Copyright (c) 2022-2024 Manuel Schneider

"""
`locate` wrapper. Note that it is up to you to ensure that the locate database is \
up to date. Pass params as necessary. The input is split using a shell lexer.
"""


import shlex
import subprocess
from pathlib import Path

from albert import *

md_iid = "3.0"
md_version = "2.0"
md_name = "Locate"
md_description = "Find and open files using locate"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/locate"
md_bin_dependencies = "locate"
md_authors = "@manuelschneid3r"


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

        self.iconUrls = [
            "xdg:preferences-system-search",
            "xdg:system-search",
            "xdg:search",
            "xdg:text-x-generic",
            f"file:{Path(__file__).parent}/locate.svg"
        ]

    def synopsis(self, query):
        return "<locate params>"

    def defaultTrigger(self):
        return "'"

    def handleTriggerQuery(self, query):
        if len(query.string) > 2:

            try:
                args = shlex.split(query.string)
            except ValueError:
                return

            result = subprocess.run(['locate', *args], stdout=subprocess.PIPE, text=True)
            if not query.isValid:
                return
            lines = sorted(result.stdout.splitlines(), reverse=True)
            if not query.isValid:
                return

            for path in lines:
                query.add(
                    StandardItem(
                        id=path,
                        text=Path(path).name,
                        subtext=path,
                        iconUrls=self.iconUrls,
                        actions=[
                            Action("open", "Open", lambda p=path: openUrl("file://%s" % p))
                        ]
                    )
                )
        else:
            query.add(
                StandardItem(
                    id="updatedb",
                    text="Update locate database",
                    subtext="Type at least three chars for a search",
                    iconUrls=self.iconUrls,
                    actions=[
                        Action("update", "Update", lambda: runTerminal("sudo updatedb"))
                    ]
                )
            )
