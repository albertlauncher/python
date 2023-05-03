# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Manuel Schneider

"""
`locate` wrapper. Note that it is up to you to ensure that the locate database is \
up to date. Pass params as necessary. The input is split using a shell lexer.
"""


from albert import *
import os
import pathlib
import shlex
import subprocess

md_iid = '1.0'
md_version = "1.8"
md_name = "Locate"
md_description = "Find and open files using locate"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/locate"
md_bin_dependencies = "locate"


class Plugin(TriggerQueryHandler):

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "'"

    def synopsis(self):
        return "<locate params>"

    def initialize(self):
        self.icons = [
            "xdg:preferences-system-search",
            "xdg:system-search",
            "xdg:search",
            "xdg:text-x-generic",
            str(pathlib.Path(__file__).parent / "locate.svg")
        ]

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
                basename = os.path.basename(path)
                query.add(
                    Item(
                        id=path,
                        text=basename,
                        subtext=path,
                        icon=self.icons,
                        actions=[
                            Action("open", "Open", lambda p=path: openUrl("file://%s" % p))
                        ]
                    )
                )
        else:
            query.add(
                Item(
                    id="updatedb",
                    text="Update locate database",
                    subtext="Type at least three chars for a search",
                    icon=self.icons,
                    actions=[
                        Action("update", "Update", lambda: runTerminal("sudo updatedb"))
                    ]
                )
            )
