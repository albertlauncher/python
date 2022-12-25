# -*- coding: utf-8 -*-

"""
Unix 'locate' wrapper extension. Note that it is up to you to ensure that the locate database is \
up to date.

This extensions is intended as secondary way to find files. Use the files extension for often used \
files and fast lookups and this extension for everything else.

Synopsis: <trigger> [filter]

where ' searches basenames and '' searches the full path  """

#  Copyright (c) 2022 Manuel Schneider

import os
import re
import subprocess
from albert import *

__iid__ = "0.5"
__version__ = "1.5"
__name__ = "Locate"
__description__ = "Find ond open files using locate"
__license__ = "BSD-3"
__url__ = "https://github.com/albertlauncher/python/tree/master/locate"
__maintainers__ = "@manuelschneid3r"
__authors__ = ["@manuelschneid3r"]
__bin_dependencies__ = ["locate"]

iconUrls = ["xdg:preferences-system-search", "xdg:system-search", "xdg:search", "xdg:text-x-generic"]


def handleQuery_(query, params):
    if len(query.string) > 2:

        result = subprocess.run(['locate', "-i", *params, query.string], stdout=subprocess.PIPE, text=True)
        lines = sorted(result.stdout.splitlines(), reverse=True)


        for path in lines:
            print(path)
            basename = os.path.basename(path)
            query.add(
                Item(
                    id=path,
                    text=basename,
                    subtext=path,
                    completion=basename,
                    icon=iconUrls,
                    actions=[
                        Action("open", "Open", lambda: openUrl("file://%s" % path))
                    ]))
    else:
        query.add(
            Item(
                id="updatedb",
                text="Update locate database",
                subtext="Type at least three chars for a search",
                completion="bla",
                icon=iconUrls,
                actions=[
                    Action("update", "Update", lambda: runTerminal(["sudo", "updatedb"]))
                ]))

class LocateBaseName(QueryHandler):
    def id(self):
        return "locate-base";
    def name(self):
        return "Locate (Base name)";
    def description(self):
        return "Find files by base name matching";
    def defaultTrigger(self):
        return "'";
    def handleQuery(self, query):
        handleQuery_(query, [])

class LocateFullPath(QueryHandler):
    def id(self):
        return "locate-full";
    def name(self):
        return "Locate (Full path)";
    def description(self):
        return "Find files by full path matching";
    def defaultTrigger(self):
        return "''";
    def handleQuery(self, query):
        handleQuery_(query, ["-b"])





class Plugin(Plugin):
    def initialize(self):
        self.exts = [LocateFullPath(), LocateBaseName()]

    def extensions(self):
        return self.exts

