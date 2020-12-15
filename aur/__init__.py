# -*- coding: utf-8 -*-

"""Query and install ArchLinux User Repository (AUR) packages.

You can search for packages and open their URLs. This extension is also intended to be used to \
quickly install the packages. If you are missing your favorite AUR helper tool send a PR.

Synopsis: <trigger> <pkg_name>"""

from albert import *
from shutil import which
from datetime import datetime
from urllib import request, parse
import json
import os
import re

__title__ = "Archlinux User Repository"
__version__ = "0.4.3"
__triggers__ = "aur "
__authors__ = "manuelschneid3r"

iconPath = os.path.dirname(__file__)+"/arch.svg"
baseurl = 'https://aur.archlinux.org/rpc/'
install_cmdline = None

if which("yaourt"):
    install_cmdline = "yaourt -S aur/%s"
elif which("pacaur"):
    install_cmdline = "pacaur -S aur/%s"
elif which("yay"):
    install_cmdline = "yay -S aur/%s"

def handleQuery(query):
    if not query.isTriggered:
        return

    query.disableSort()

    stripped = query.string.strip()

    if stripped:
        params = {
            'v': '5',
            'type': 'search',
            'by': 'name',
            'arg': stripped
        }
        url = "%s?%s" % (baseurl, parse.urlencode(params))
        req = request.Request(url)

        with request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data['type'] == "error":
                return Item(
                    id=__title__,
                    icon=iconPath,
                    text="Error",
                    subtext=data['error']
                )
            else:
                results = []
                pattern = re.compile(query.string, re.IGNORECASE)
                results_json = data['results']
                results_json.sort(key=lambda item: item['Name'])
                results_json.sort(key=lambda item: len(item['Name']))

                for entry in results_json:
                    name = entry['Name']
                    item = Item(
                        id = __title__,
                        icon = iconPath,
                        text = "<b>%s</b> <i>%s</i> (%s)" % (pattern.sub(lambda m: "<u>%s</u>" % m.group(0), name), entry['Version'], entry['NumVotes']),
                        completion = "%s%s" % (__triggers__, name)
                    )
                    subtext = entry['Description'] if entry['Description'] else "[No description]"
                    if entry['OutOfDate']:
                        subtext = '<font color="red">[Out of date: %s]</font> %s' % (datetime.fromtimestamp(entry['OutOfDate']).strftime("%F"), subtext)
                    if entry['Maintainer'] is None:
                        subtext = '<font color="red">[Orphan]</font> %s' % subtext
                    item.subtext = subtext

                    if install_cmdline:
                        pkgmgr = install_cmdline.split(" ", 1)
                        item.actions = [
                            TermAction("Install using %s" % pkgmgr[0], install_cmdline % name),
                            TermAction("Install using %s (noconfirm)" % pkgmgr[0], install_cmdline % name + " --noconfirm")                        
                        ]

                    item.addAction(UrlAction("Open AUR website", "https://aur.archlinux.org/packages/%s/" % name))

                    if entry['URL']:
                        item.addAction(UrlAction("Open project website", entry['URL']))

                    results.append(item)
                return results
    else:
        return Item(id=__title__,
                    icon=iconPath,
                    text=__title__,
                    subtext="Enter a query to search the AUR",
                    actions=[UrlAction("Open AUR packages website", "https://aur.archlinux.org/packages/")])
