# -*- coding: utf-8 -*-

"""Arch Linux Package Manager (pacman) extension.

The extension provides a way to install, remove and search for packages in the archlinux.org \
database. If no search query is supplied, you have the option to do a system update. \
Otherwise albert will try to find for packages matching the filter. For more information about \
`pacman` please have a look at: https://wiki.archlinux.org/index.php/pacman

Synopsis: <trigger> [filter]"""

import re
import subprocess
from shutil import which

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "PacMan"
__version__ = "1.2"
__trigger__ = "pacman "
__author__ = "Manuel Schneider, Benedict Dudel"
__dependencies__ = ["pacman", "expac"]

for dep in __dependencies__:
    if which(dep) is None:
        raise Exception("'%s' is not in $PATH." % dep)

for iconName in ["archlinux-logo", "system-software-install"]:
    iconPath = iconLookup(iconName)
    if iconPath:
        break

def handleQuery(query):
    if query.isTriggered:
        if not query.string.strip():
            return Item(
                id="%s-update" % __prettyname__,
                icon=iconPath,
                text="Pacman package manager",
                subtext="Enter the name of the package you are looking for",
                completion=__trigger__
            )

        items = []
        pattern = re.compile(query.string, re.IGNORECASE)
        proc = subprocess.Popen(["expac", "-Ss", "%n\n%v\n%r\n%d\n%u\n%E", query.string],
                                stdout=subprocess.PIPE)
        for line in proc.stdout:
            name = line.decode().rstrip()
            vers = proc.stdout.readline().decode().rstrip()
            repo = proc.stdout.readline().decode().rstrip()
            desc = proc.stdout.readline().decode().rstrip()
            purl = proc.stdout.readline().decode().rstrip()
            deps = proc.stdout.readline().decode().rstrip()

            items.append(Item(
                id="%s%s%s" % (__prettyname__, repo, name),
                icon=iconPath,
                text="<b>%s</b> <i>%s</i> [%s]" % (pattern.sub(lambda m: "<u>%s</u>" % m.group(0), name), vers, repo),
                subtext="%s <i>(<b>%s</b>)</i>" % (pattern.sub(lambda m: "<u>%s</u>" % m.group(0), desc), deps) if deps else pattern.sub(lambda m: "<u>%s</u>" % m.group(0), desc),
                completion="%s%s" % (query.trigger, name),
                actions=[
                    TermAction("Install", ["sudo", "pacman", "-S", name]),
                    TermAction("Remove", ["sudo", "pacman", "-Rs", name]),
                    UrlAction("Show on packages.archlinux.org",
                              "https://www.archlinux.org/packages/%s/x86_64/%s/" % (repo, name)),
                    UrlAction("Show project website", purl)
                ]
            ))

        if not items:
            return Item(
                id="%s-empty" % __prettyname__,
                icon=iconPath,
                text="Search on archlinux.org",
                subtext="No results found in the local database",
                completion=__trigger__,
                actions=[
                    UrlAction("Search on archlinux.org",
                              "https://www.archlinux.org/packages/?q=%s" % query.string.strip())
                ]
            )

        return items

    elif len(query.string.strip()) > 0 and ("pacman".startswith(query.string.lower()) or "update".startswith(query.string.lower())):
        return Item(
            id="%s-update" % __prettyname__,
            icon=iconPath,
            text="Update all packages on the system",
            subtext="Synchronizes the repository databases and updates the system's packages",
            completion=__trigger__,
            actions=[TermAction("Update the system", ["sudo", "pacman", "-Syu"])]
        )
