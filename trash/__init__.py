# -*- coding: utf-8 -*-

"""
This extension provides a single item which opens the
systems trash location in your default file manager.
"""

#  Copyright (c) 2023 Manuel Schneider

from albert import *
import os
from platform import system
from pathlib import Path

md_iid = "0.5"
md_version = "1.2"
md_name = "Trash"
md_description = "Open trash"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/trash"
md_maintainers = "@manuelschneid3r"

class Plugin(QueryHandler):
    def id(self):
        return __name__

    def name(self):
        return md_name

    def description(self):
        return md_description

    def initialize(self):
        if (system() == 'Linux'):
            trash_path  = "trash:///"
            icon = ["xdg:user-trash-full", os.path.dirname(__file__)+"/trash.svg"]
        elif (system() == 'Darwin'):
            trash_path  = "file://%s/.Trash" % Path.home()
            icon = [os.path.dirname(__file__)+"/trash.svg"]
        else:
            raise NotImplementedError("%1 not supported" % system())

        self.trash_item = Item(id="trash-open",
                               text="Trash",
                               subtext="Open trash folder",
                               icon=icon,
                               actions=[Action("trash-open", "Open trash", lambda path=trash_path: openUrl(path))])

    def handleQuery(self, query):
        query.add(self.trash_item)