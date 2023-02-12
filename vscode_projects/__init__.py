"""
This extension make it possible search VSCode Projects by albert
"""

from albert import *
import os

import json
import urllib.parse

md_iid = "0.5"
md_version = "1.0"
md_name = "VSCode projects"
md_description = "Open VSCode projects"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/vscode_projects"
md_maintainers = "@cathaysia"
md_credits = "Original idea by Longtao Zhang"

vsc_db = "~/.config/Code/User/globalStorage/state.vscdb"
vsc_storage = "~/.config/Code/User/globalStorage/storage.json"
vsc_workspace = "~/.config/Code/User/workspaceStorage/"


class Plugin(QueryHandler):
    icon_path = "xdg:code"

    def id(self):
        return md_iid

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "vsc "

    def handleQuery(self, query):
        if not query.isValid:
            return
        query_str: str = query.string
        results = []
        for dirpath, dirnames, filenames in os.walk(os.path.expanduser(vsc_workspace)):
            for file_name in filenames:
                if file_name != "workspace.json":
                    continue
                with open(os.path.join(dirpath, file_name), "r") as f:
                    full_prj_path: str = urllib.parse.unquote(
                        json.loads(f.read())["folder"]
                    )
                    full_prj_path = full_prj_path.replace("file://", "")
                    if query_str != " " and not full_prj_path.__contains__(query_str):
                        continue
                    results.append(
                        Item(
                            id="kill",
                            icon=[self.icon_path],
                            text=os.path.basename(full_prj_path),
                            subtext=full_prj_path,
                            actions=[
                                Action(
                                    "Open",
                                    "Open project by VSCode",
                                    lambda pro=full_prj_path: runDetachedProcess(
                                        ["code", pro]
                                    ),
                                ),
                            ],
                        )
                    )
        query.add(results)

