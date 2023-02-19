"""
This extension make it possible search VSCode Projects by albert
"""

from albert import *
import json
import os
import platform
import sqlite3
import urllib.parse

md_iid = "0.5"
md_version = "1.0"
md_name = "VSCode projects"
md_description = "Open VSCode projects"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/vscode_projects"
md_maintainers = "@cathaysia"
md_credits = "Original idea by Longtao Zhang"


class Plugin(QueryHandler):
    icon_path = "xdg:code"
    os_prefix = "~" if platform.system().lower() != "window" else os.getenv("APPDATA") or ""
    db = os.path.expanduser(os_prefix + "/.config/Code/User/globalStorage/state.vscdb")
    storage = os.path.expanduser(os_prefix + "/.config/Code/User/globalStorage/storage.json")
    workspace = os.path.expanduser(os_prefix + "/.config/Code/User/workspaceStorage/")

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "vsc "

    def handleQuery(self, query):
        if not query.isValid:
            return
        results = []

        con = sqlite3.connect(self.db)
        cur = con.cursor()
        cur.execute(
            'SELECT value FROM ItemTable WHERE key = "history.recentlyOpenedPathsList"'
        )

        for row in cur:
            j = json.loads(row[0])
            for item in j["entries"]:
                uri = ""
                if "folderUri" in item:
                    uri = item["folderUri"]
                else:
                    uri = item["fileUri"]
                uri = uri.replace("file://", "")
                uri = urllib.parse.unquote(uri)
                results.append(
                    Item(
                        id=md_id,
                        icon=[self.icon_path],
                        text=os.path.basename(uri),
                        subtext=uri,
                        actions=[
                            Action(
                                "Open",
                                "Open project by VSCode",
                                lambda pro=uri: runDetachedProcess(["code", pro]),
                            ),
                        ],
                    )
                )
        query.add(results)
