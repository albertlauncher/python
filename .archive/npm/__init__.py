# -*- coding: utf-8 -*-

"""Install, remove and search packages in the npmjs.com database.

If no search query is supplied you have the option to update all globally installed packages.

Synopsis: <trigger> [filter]"""

#  Copyright (c) 2022 Manuel Schneider

from albert import *
import os
import json
import subprocess

__title__ = "npm"
__version__ = "0.4.0"
__triggers__ = "npm "
__authors__ = "Benedict Dudel"
__exec_deps__ = ["npm"]

iconPath = iconLookup("npm") or os.path.dirname(__file__)+"/logo.svg"

def handleQuery(query):
    if query.isTriggered:
        if not query.string.strip():
            return Item(
                id = __title__,
                icon = iconPath,
                text = "Update",
                subtext = "Update all globally installed packages",
                actions = [
                    TermAction("Update packages", ["npm", "update", "--global"])
                ]
            )

        items = getSearchResults(query.string.strip())
        if not items:
            return Item(
                id = __title__,
                icon = iconPath,
                text = "Search on npmjs.com",
                subtext = "No modules found in local database. Try to search on npmjs.com",
                actions = [
                    UrlAction(
                        "Search on npmjs.com",
                        "https://www.npmjs.com/search?q=%s" % query.string.strip()
                    )
                ]
            )

        return items

def getSearchResults(query):
    proc = subprocess.run(["npm", "search", "--json", query], stdout=subprocess.PIPE)

    items = []
    for module in json.loads(proc.stdout.decode()):
        items.append(
            Item(
                id = __title__,
                icon = iconPath,
                text = "%s (%s)" % (module["name"], module["version"]),
                subtext = module.get("description", ""),
                actions = [
                    UrlAction("Open module on npmjs.com", "https://www.npmjs.com/package/%s" % module["name"]),
                    TermAction("Install", ["npm", "install", "--global", module["name"]]),
                    TermAction("Update", ["npm", "update", "--global", module["name"]]),
                    TermAction("Remove", ["npm", "uninstall", "--global", module["name"]]),
                ]
            )
        )

    return items
