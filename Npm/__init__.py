"""Extension for the JavaScript package manager `npm`

The extension provides a way to install, remove and search for packages in the
npmjs.com database. To trigger the extension you just need to type `npm `
in albert.

If no search query is supplied you have the option to update all globally
installed packages.
"""

from albertv0 import *
from shutil import which
import os
import json
import subprocess


__iid__ = "PythonInterface/v0.1"
__prettyname__ = "npm"
__version__ = "1.0"
__trigger__ = "npm "
__author__ = "Benedict Dudel"
__dependencies__ = ["npm"]


if which("npm") is None:
    raise Exception("'npm' is not in $PATH.")

iconPath = iconLookup("npm")
if not iconPath:
    iconPath = os.path.dirname(__file__)+"/logo.svg"


def handleQuery(query):
    if query.isTriggered:
        if not query.string.strip():
            return Item(
                id = __prettyname__,
                icon = iconPath,
                text = "Update",
                subtext = "Update all globally installed packages",
                actions = [
                    TermAction("", ["npm", "update", "--global"])
                ]
            )

        items = getSearchResults(query.string.strip())
        if not items:
            return Item(
                id = __prettyname__,
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
                id = __prettyname__,
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
