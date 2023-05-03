# -*- coding: utf-8 -*-
#  Copyright (c) 2022-2023 Manuel Schneider

"""
Search for packages and open their URLs. This extension is also intended to be used to \
quickly install the packages. If you are missing your favorite AUR helper tool send a PR.
"""

from albert import *
from shutil import which
from datetime import datetime
from urllib import request, parse
from time import sleep
import json
import os

md_iid = '1.0'
md_version = "1.7"
md_name = "AUR"
md_description = "Query and install AUR packages"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/aur"
md_maintainers = "@manuelschneid3r"


class Plugin(TriggerQueryHandler):

    aur_url = "https://aur.archlinux.org/packages/"
    baseurl = 'https://aur.archlinux.org/rpc/'

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "aur "

    def initialize(self):
        self.icon = [os.path.dirname(__file__)+"/arch.svg"]

        if which("yaourt"):
            self.install_cmdline = "yaourt -S aur/%s"
        elif which("pacaur"):
            self.install_cmdline = "pacaur -S aur/%s"
        elif which("yay"):
            self.install_cmdline = "yay -S aur/%s"
        elif which("paru"):
            self.install_cmdline = "paru -S aur/%s"
        else:
            info("No supported AUR helper found.")
            self.install_cmdline = None

    def handleTriggerQuery(self, query):
        for number in range(50):
            sleep(0.01)
            if not query.isValid:
                return

        stripped = query.string.strip()
        if stripped:
            params = {
                'v': '5',
                'type': 'search',
                'by': 'name',
                'arg': stripped
            }
            url = "%s?%s" % (self.baseurl, parse.urlencode(params))
            req = request.Request(url)

            with request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                if data['type'] == "error":
                    query.add(Item(
                        id=md_id,
                        text="Error",
                        subtext=data['error'],
                        icon=self.icon
                    ))
                else:
                    results = []
                    results_json = data['results']
                    results_json.sort(key=lambda i: i['Name'])
                    results_json.sort(key=lambda i: len(i['Name']))

                    for entry in results_json:
                        name = entry['Name']
                        item = Item(
                            id = md_id,
                            icon = self.icon,
                            text = f"{entry['Name']} {entry['Version']}"
                        )

                        subtext = f"☆{entry['NumVotes']}"
                        if entry['Maintainer'] is None:
                            subtext += ', Unmaintained!'
                        if entry['OutOfDate']:
                            subtext += ', Out of date: %s' % datetime.fromtimestamp(entry['OutOfDate']).strftime("%F")
                        if entry['Description']:
                            subtext += ', %s' % entry['Description']
                        item.subtext = subtext

                        actions = []
                        if self.install_cmdline:
                            pacman = self.install_cmdline.split(" ", 1)[0]
                            actions.append(Action(
                                id="inst",
                                text="Install using %s" % pacman,
                                callable=lambda n=name: runTerminal(
                                    script=self.install_cmdline % n,
                                    close_on_exit=False
                                )
                            ))
                            actions.append(Action(
                                id="instnc",
                                text="Install using %s (noconfirm)" % pacman,
                                callable=lambda n=name: runTerminal(
                                    script=self.install_cmdline % n + " --noconfirm",
                                    close_on_exit=False
                                )
                            ))

                        actions.append(Action("open-aursite", "Open AUR website",
                                              lambda n=name: openUrl(f"{self.aur_url}{n}/")))

                        if entry['URL']:
                            actions.append(Action("open-website", "Open project website",
                                                  lambda u=entry['URL']: openUrl(u)))

                        item.actions = actions
                        results.append(item)

                    query.add(results)
        else:
            query.add(Item(
                id=md_id,
                text=md_name,
                subtext="Enter a query to search the AUR",
                icon=self.icon,
                actions=[Action("open-aur", "Open AUR packages website", lambda: openUrl(self.aur_url))]
            ))
