"""
Extension for the package manager `pacman`

The extension provides a way to install, remove and search for packages in the
archlinux.org database. To trigger the extension you just need to type `pacman `
in albert.

If no search query is supplied you have the option to do a system update.
Otherwise albert will try to search for packages with the search query within
the package name.

For more information about `pacman` please have a look at:
    - https://wiki.archlinux.org/index.php/pacman
"""

import os
import subprocess
import re
from albertv0 import *
from shutil import which

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "pacman"
__version__ = "1.0"
__trigger__ = "pacman "
__author__ = "Benedict Dudel"
__dependencies__ = ["pacman"]


if which("pacman") is None:
    raise Exception("'pacman' is not in $PATH.")

iconPath = "system-software-install"


def handleQuery(query):
    if query.isTriggered:
        if not query.string.strip():
            return [Item(
                id = __prettyname__,
                icon = iconPath,
                text = "Update all packages on the system",
                subtext = "Synchronizes the repository databases and updates the system's packages",
                completion = __trigger__,
                actions = [
                    TermAction(
                        text = "Update all packages",
                        commandline = ["pacman", "-Syu"]
                    ),
                ]
            )]

        packages = getPackages(query.string.strip())
        items = []
        for package in packages:
            items.append(Item(
                id = package["package"],
                icon = iconPath,
                text = package["name"],
                subtext = package["package"],
                completion = "%s%s" % (__trigger__, package["name"]),
                actions = [
                    TermAction(
                        text = "Install",
                        commandline = ["pacman", "-S", package["name"]]
                    ),
                    TermAction(
                        text = "Remove",
                        commandline = ["pacman", "-Rs", package["name"]]
                    ),
                    UrlAction(
                        text = "Search on archlinux.org",
                        url = "https://www.archlinux.org/packages/?q=%s" % package["name"]
                    )
                ]
            ))

        if len(items) <= 0:
            return [Item(
                id = __prettyname__,
                icon = iconPath,
                text = "Search on archlinux.org",
                subtext = "No results found in the local database",
                completion = __trigger__,
                actions = [
                    UrlAction(
                        text = "Search on archlinux.org",
                        url = "https://www.archlinux.org/packages/?q=%s" % query.string.strip()
                    )
                ]
            )]

        return items

def getPackages(query):
    items = []

    result = subprocess.Popen(["pacman", "-Ss", query], stdout=subprocess.PIPE)
    lines = result.stdout.readlines()

    line = 0
    while line < len(lines):
        result = re.search("/(.*)\s", lines[line].decode("utf-8").strip())
        if result and result.group(1) and query in result.group(1):
            items.append({
                "name": result.group(1),
                "package": lines[line].decode("utf-8").strip(),
                "description": lines[line + 1].decode("utf-8").strip()
            })

        line = line + 2

    return items
