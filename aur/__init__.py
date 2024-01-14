# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

"""
Search for packages and open their URLs. This extension is also intended to be used to \
quickly install the packages. If you are missing your favorite AUR helper tool send a PR.
"""

import json
from datetime import datetime
from pathlib import Path
from shutil import which
from time import sleep
from urllib import request, parse

from albert import *

md_iid = '2.2'
md_version = "1.9"
md_name = "AUR"
md_description = "Query and install AUR packages"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/master/aur"
md_authors = "@manuelschneid3r"


class Plugin(PluginInstance, TriggerQueryHandler):

    aur_url = "https://aur.archlinux.org/packages/"
    baseurl = 'https://aur.archlinux.org/rpc/'

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     defaultTrigger='aur ')
        PluginInstance.__init__(self, extensions=[self])

        self.iconUrls = [f"file:{Path(__file__).parent}/arch.svg"]

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

    def configWidget(self):
        return [
            {
                'type': 'label',
                'text': __doc__.strip()
            }
        ]

    def handleTriggerQuery(self, query):
        for _ in range(50):
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
                    query.add(StandardItem(
                        id=md_id,
                        text="Error",
                        subtext=data['error'],
                        iconUrls=self.iconUrls
                    ))
                else:
                    results = []
                    results_json = data['results']
                    results_json.sort(key=lambda i: i['Name'])
                    results_json.sort(key=lambda i: len(i['Name']))

                    for entry in results_json:
                        name = entry['Name']
                        item = StandardItem(
                            id=md_id,
                            iconUrls=self.iconUrls,
                            text=f"{entry['Name']} {entry['Version']}"
                        )

                        subtext = f"⭐{entry['NumVotes']}"
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
            query.add(StandardItem(
                id=md_id,
                text=md_name,
                subtext="Enter a query to search the AUR",
                iconUrls=self.iconUrls,
                actions=[Action("open-aur", "Open AUR packages website", lambda: openUrl(self.aur_url))]
            ))
