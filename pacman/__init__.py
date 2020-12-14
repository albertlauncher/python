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

from albert import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "PacMan"
__version__ = "1.3"
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
                id="%s-update" % __name__,
                icon=iconPath,
                text="Pacman package manager",
                subtext="Enter the name of the package you are looking for",
                completion=__trigger__,
                actions=[
                    TermAction("Update the system (no confirm)", ["sudo", "pacman", "-Syu", "--noconfirm"]),
                    TermAction("Update the system", ["sudo", "pacman", "-Syu"])
                ]
            )

        # Get data. Results are sorted so we can merge in O(n)
        proc_s = subprocess.Popen(["expac", "-Ss", "%n\t%v\t%r\t%d\t%u\t%E", query.string], stdout=subprocess.PIPE, universal_newlines=True)
        proc_q = subprocess.Popen(["expac", "-Qs", "%n", query.string], stdout=subprocess.PIPE, universal_newlines=True)
        proc_q.wait()

        def next_stripped(it):
            n = next(it, None)
            if n:
                n = n.rstrip("\n")
            return n


        items = []
        pattern = re.compile(query.string, re.IGNORECASE)
        local_iter = iter(proc_q.stdout.readline, '')
        next_local_package = next_stripped(local_iter)
        for line in proc_s.stdout:

            # Parse data
            pkg_name, pkg_vers, pkg_repo, pkg_desc, pkg_purl, pkg_deps = line.rstrip("\n").split("\t")
            pkg_installed = next_local_package == pkg_name
            if next_local_package == pkg_name:
                next_local_package = next_stripped(local_iter)

            # Create item
            item = Item(
                id="%s:%s:%s" % (__name__, pkg_repo, pkg_name),
                icon=iconPath,
                text="<b>%s</b> <i>%s</i> [%s]" % (pattern.sub(lambda m: "<u>%s</u>" % m.group(0), pkg_name), pkg_vers, pkg_repo),
                subtext="%s%s <i>(<b>%s</b>)</i>" % ("[Installed] " if pkg_installed else "", pattern.sub(lambda m: "<u>%s</u>" % m.group(0), pkg_desc), pkg_deps) if pkg_deps else pattern.sub(lambda m: "<u>%s</u>" % m.group(0), pkg_desc),
                completion="%s%s" % (query.trigger, pkg_name)
            )
            items.append(item)

            actions = []
            if pkg_installed:
                item.addAction(TermAction("Remove", ["sudo", "pacman", "-Rs", pkg_name]))
                item.addAction(TermAction("Reinstall", ["sudo", "pacman", "-S", pkg_name]))
            else:
                item.addAction(TermAction("Install", ["sudo", "pacman", "-S", pkg_name]))
            item.addAction(UrlAction("Show on packages.archlinux.org", "https://www.archlinux.org/packages/%s/x86_64/%s/" % (pkg_repo, pkg_name)))
            if pkg_purl:
                item.addAction(UrlAction("Show project website", pkg_purl))

        if items:
            return items
        else:
            return Item(
                id="%s-empty" % __name__,
                icon=iconPath,
                text="Search on archlinux.org",
                subtext="No results found in the local database",
                completion=__trigger__,
                actions=[
                    UrlAction("Search on archlinux.org",
                              "https://www.archlinux.org/packages/?q=%s" % query.string.strip())
                ]
            )

    elif len(query.string.strip()) > 0 and ("pacman".startswith(query.string.lower()) or "update".startswith(query.string.lower())):
        return Item(
            id="%s-update" % __name__,
            icon=iconPath,
            text="Update all packages on the system",
            subtext="Synchronizes the repository databases and updates the system's packages",
            completion=__trigger__,
            actions=[
                TermAction("Update the system (no confirm)", ["sudo", "pacman", "-Syu", "--noconfirm"]),
                TermAction("Update the system", ["sudo", "pacman", "-Syu"])
            ]
        )
