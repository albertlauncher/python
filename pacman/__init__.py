# -*- coding: utf-8 -*-

"""
This plugin is a `pacman` (Arch Linux Package Manager) wrapper. You can update, search, install and remove \
packages.
"""

import subprocess
from time import sleep
import pathlib

from albert import Action, Item, TriggerQueryHandler, runTerminal, openUrl

md_iid = '1.0'
md_version = "1.7"
md_name = "PacMan"
md_description = "Search, install and remove packages"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/pacman"
md_bin_dependencies = ["pacman", "expac"]


class Plugin(TriggerQueryHandler):

    pkgs_url = "https://www.archlinux.org/packages/"

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def synopsis(self):
        return "<package name>"

    def defaultTrigger(self):
        return "pac "

    def initialize(self):
        self.icons = [
            "xdg:archlinux-logo",
            "xdg:system-software-install",
            str(pathlib.Path(__file__).parent / "arch.svg")
        ]

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()

        # Update item on empty queries
        if not stripped:
            query.add(Item(
                id="%s-update" % md_id,
                text="Pacman package manager",
                subtext="Enter the package you are looking for or hit enter to update.",
                icon=self.icons,
                actions=[
                    Action("up-nc", "Update packages (no confirm)",
                           lambda: runTerminal("sudo pacman -Syu --noconfirm")),
                    Action("up", "Update packages", lambda: runTerminal("sudo pacman -Syu")),
                    Action("up-cache", "Update pacman cache", lambda: runTerminal("sudo pacman -Sy"))
                ]
            ))
            return

        # avoid rate limiting
        for number in range(50):
            sleep(0.01)
            if not query.isValid:
                return

        # Get data. Results are sorted, so we can merge in O(n)
        proc_s = subprocess.Popen(["expac", "-Ss", "%n\t%v\t%r\t%d\t%u\t%E", stripped],
                                  stdout=subprocess.PIPE, universal_newlines=True)
        proc_q = subprocess.Popen(["expac", "-Qs", "%n", stripped], stdout=subprocess.PIPE, universal_newlines=True)
        proc_q.wait()

        items = []
        local_pkgs = set(proc_q.stdout.read().split('\n'))
        remote_pkgs = [tuple(line.split('\t')) for line in proc_s.stdout.read().split('\n')[:-1]]  # newline at end

        for pkg_name, pkg_vers, pkg_repo, pkg_desc, pkg_purl, pkg_deps in remote_pkgs:
            if stripped not in pkg_name :
                continue

            pkg_installed = True if pkg_name in local_pkgs else False

            actions = []
            if pkg_installed:
                actions.extend([
                    Action("rem", "Remove", lambda n=pkg_name: runTerminal("sudo pacman -Rs %s" % n)),
                    Action("reinst", "Reinstall", lambda n=pkg_name: runTerminal("sudo pacman -S %s" % n))
                ])
            else:
                actions.append(Action("inst", "Install", lambda n=pkg_name: runTerminal("sudo pacman -S %s" % n)))
            actions.append(Action("pkg_url", "Show on packages.archlinux.org",
                                  lambda r=pkg_repo, n=pkg_name: openUrl(f"{r}/x86_64/{n}/")))
            if pkg_purl:
                actions.append(Action("proj_url", "Show project website", lambda u=pkg_purl: openUrl(u)))

            item = Item(
                id="%s_%s_%s" % (md_id, pkg_repo, pkg_name),
                icon=self.icons,
                text="%s %s [%s]" % (pkg_name, pkg_vers, pkg_repo),
                subtext=f"{pkg_desc} [Installed]" if pkg_installed else f"{pkg_desc}",
                completion="%s%s" % (query.trigger, pkg_name),
                actions=actions
            )
            items.append(item)

        if items:
            query.add(items)
        else:
            query.add(Item(
                id="%s-empty" % md_id,
                text="Search on archlinux.org",
                subtext="No results found in the local database",
                icon=self.icons,
                actions=[Action("search", "Search on archlinux.org", lambda: openUrl(f"{self.pkgs_url}?q={stripped}"))]
            ))
