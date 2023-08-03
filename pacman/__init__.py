# -*- coding: utf-8 -*-

"""
This plugin is a `pacman` (Arch Linux Package Manager) wrapper. You can update, search, install and remove \
packages.
"""

import subprocess
from time import sleep
import pathlib

from albert import Action, Item, TriggerQueryHandler, runTerminal, openUrl

md_iid = '2.0'
md_version = "1.8"
md_name = "PacMan"
md_description = "Search, install and remove packages"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/pacman"
md_bin_dependencies = ["pacman", "expac"]


class Plugin(PluginInstance, TriggerQueryHandler):

    pkgs_url = "https://www.archlinux.org/packages/"

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis='<package name>',
                                     defaultTrigger='pac ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [
            "xdg:archlinux-logo",
            "xdg:system-software-install",
            f"file:{pathlib.Path(__file__).parent}/arch.svg"
        ]

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()

        # Update item on empty queries
        if not stripped:
            query.add(StandardItem(
                id="%s-update" % md_id,
                text="Pacman package manager",
                subtext="Enter the package you are looking for or hit enter to update.",
                iconUrls=self.iconUrls,
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
            if stripped not in pkg_name:
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

            item = StandardItem(
                id="%s_%s_%s" % (md_id, pkg_repo, pkg_name),
                iconUrls=self.iconUrls,
                text="%s %s [%s]" % (pkg_name, pkg_vers, pkg_repo),
                subtext=f"{pkg_desc} [Installed]" if pkg_installed else f"{pkg_desc}",
                inputActionText="%s%s" % (query.trigger, pkg_name),
                actions=actions
            )
            items.append(item)

        if items:
            query.add(items)
        else:
            query.add(StandardItem(
                id="%s-empty" % md_id,
                text="Search on archlinux.org",
                subtext="No results found in the local database",
                iconUrls=self.iconUrls,
                actions=[Action("search", "Search on archlinux.org", lambda: openUrl(f"{self.pkgs_url}?q={stripped}"))]
            ))
