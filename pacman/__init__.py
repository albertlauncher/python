# -*- coding: utf-8 -*-

"""Arch Linux Package Manager (pacman) extension.

The extension provides a way to install, remove and search for packages in the archlinux.org \
database. If no search query is supplied, you have the option to do a system update. \
Otherwise albert will try to find for packages matching the filter. For more information about \
`pacman` please have a look at: https://wiki.archlinux.org/index.php/pacman

Synopsis: <trigger> [filter]"""

import re
import subprocess
import time

from albert import TermAction, iconLookup, Item, UrlAction

__title__ = "PacMan"
__version__ = "0.4.4"
__triggers__ = "pacman "
__authors__ = ["Manuel Schneider", "Benedict Dudel"]
__exec_deps__ = ["pacman", "expac"]

iconPath = iconLookup(["archlinux-logo", "system-software-install"])


def handleQuery(query):
    if query.isTriggered:
        if not query.string.strip():
            return Item(
                id="%s-update" % __name__,
                icon=iconPath,
                text="Pacman package manager",
                subtext="Enter the package you are looking for or hit enter to update.",
                completion=__triggers__,
                actions=[
                    TermAction("Update the system (no confirm)", "sudo pacman -Syu --noconfirm"),
                    TermAction("Update the system", "sudo pacman -Syu")
                ]
            )

        time.sleep(0.1)
        if not query.isValid:
            return

        # Get data. Results are sorted so we can merge in O(n)
        proc_s = subprocess.Popen(["expac", "-Ss", "%n\t%v\t%r\t%d\t%u\t%E", query.string],
                                  stdout=subprocess.PIPE, universal_newlines=True)
        proc_q = subprocess.Popen(["expac", "-Qs", "%n", query.string], stdout=subprocess.PIPE, universal_newlines=True)
        proc_q.wait()

        items = []
        pattern = re.compile(query.string, re.IGNORECASE)
        local_pkgs = set(proc_q.stdout.read().split('\n'))
        remote_pkgs = [tuple(line.split('\t')) for line in proc_s.stdout.read().split('\n')[:-1]]  # newline at end

        for pkg_name, pkg_vers, pkg_repo, pkg_desc, pkg_purl, pkg_deps in remote_pkgs:
            if not pattern.search(pkg_name):
                continue

            pkg_installed = True if pkg_name in local_pkgs else False

            item = Item(
                id="%s:%s:%s" % (__name__, pkg_repo, pkg_name),
                icon=iconPath,
                text="%s <i>%s</i> [%s]"
                     % (pattern.sub(lambda m: "<u>%s</u>" % m.group(0), pkg_name), pkg_vers, pkg_repo),
                subtext=("<b>[Installed]</b> %s%s" if pkg_installed else "%s%s")
                        % (pkg_desc, (" <i>(%s)</i>" % pkg_deps) if pkg_deps else ""),
                completion="%s%s" % (query.trigger, pkg_name)
            )
            items.append(item)

            if pkg_installed:
                item.addAction(TermAction("Remove", "sudo pacman -Rs %s" % pkg_name))
                item.addAction(TermAction("Reinstall", "sudo pacman -S %s" % pkg_name))
            else:
                item.addAction(TermAction("Install", "sudo pacman -S %s" % pkg_name))
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
            actions=[
                TermAction("Update the system (no confirm)", "sudo pacman -Syu --noconfirm"),
                TermAction("Update the system", "sudo pacman -Syu")
            ]
        )
