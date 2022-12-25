# -*- coding: utf-8 -*-

"""
broken
"""
#  Copyright (c) 2022 Manuel Schneider

import albert
from albert import *
from time import sleep
import io
import os
import subprocess
from pathlib import Path

__iid__ = "0.5"
__version__ = "1.0"
__id__ = "find"
__name__ = "Find"
__description__ = "Online search your file system"
__license__ = "BSD-3"
__url__ = "https://github.com/albertlauncher/python/tree/master/find"
__maintainers__ = "@manuelschneid3r"
__authors__ = ["@manuelschneid3r"]
__bin_dependencies__ = ["find"]
__default_trigger__ = "find "
__synopsis__ = "<pattern>"


class Plugin(Plugin, QueryHandler):
    def __init__(self):
        albert.Plugin.__init__(self)
        albert.QueryHandler.__init__(self)

    def id(self):
        return __id__;

    def name(self):
        return __name__;

    def takeThisAndModifyR(self, item):
        item.id = "takeThisAndModifyR";

    def takeThisAndModifyR_(self, item):
        item.id = "takeThisAndModifyR_";

    def takeThisAndModifyP(self, item):
        item.id = "takeThisAndModifyP";

    def description(self):
        return __description__;

    def handleQuery(self, query):
        info(query.string)
        proc = subprocess.Popen(["find", Path.home(), "iname", query.string], stdout=subprocess.PIPE)
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            absolute = os.path.abspath(line)
            item = Item(
                id=absolute,
                text=os.path.basename(absolute),
                subtext=absolute,
                completion="",
                icon=[":python"],
                actions=[
                    Action(
                        id="clip",
                        text="setClipboardText (ClipAction)",
                        callable=lambda: setClipboardText(text=configLocation())
                    )
                ]
            )
            query.add(item)


    def initialize(self):
        info("Find::initialize")

#    def extensions(self):
#        return [self.e]
##        pass
