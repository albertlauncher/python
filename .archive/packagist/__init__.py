# -*- coding: utf-8 -*-

"""Search for PHP packages on Packagist.

To install packages you need to have installed composer. By default this extension will search by \
package name. But searching for packages by type or tag is supported as well.

Synopsis: <trigger> [tag|type] <filter>"""

#  Copyright (c) 2022 Manuel Schneider

from albert import *
import os
import json
import urllib.request

__title__ = "Packagist"
__version__ = "0.4.0"
__triggers__ = "packagist "
__authors__ = "Benedict Dudel"
__exec_deps__ = ["composer"]

iconPath = os.path.dirname(__file__)+"/logo.png"


def handleQuery(query):
    if query.isTriggered:
        if not query.string.strip():
            return [
                Item(
                    id = "packagist-search-by-tag",
                    icon = iconPath,
                    text = "by tag",
                    subtext = "Searching for packages by tag",
                    completion = "%stag " % __triggers__,
                    actions=[]
                ),
                Item(
                    id = "packagist-search-by-type",
                    icon = iconPath,
                    text = "by type",
                    subtext = "Searching for packages by type",
                    completion = "%stype " % __triggers__,
                    actions=[]
                )
            ]

        if query.string.strip().startswith("tag "):
            if query.string.strip()[4:]:
                return getItems("https://packagist.org/search.json?tags=%s" % query.string.strip()[4:])

        if query.string.strip().startswith("type "):
            if query.string.strip()[5:]:
                return getItems("https://packagist.org/search.json?type=%s" % query.string.strip()[5:])

        return getItems("https://packagist.org/search.json?q=%s" % query.string)

def getItems(url):
    items = []
    with urllib.request.urlopen(url) as uri:
        packages = json.loads(uri.read().decode())
        for package in packages['results']:
            items.append(
                Item(
                    id = "packagist-package-%s" % package["name"],
                    icon = iconPath,
                    text = package["name"],
                    subtext = package["description"],
                    completion = "%sname %s" % (__triggers__, package["name"]),
                    actions = [
                        UrlAction(
                            text = "Open on packagist.org",
                            url = package["url"]
                        ),
                        UrlAction(
                            text = "Open url of repository",
                            url = package["repository"]
                        ),
                        TermAction(
                            text = "Install",
                            commandline = ["composer", "global", "require", package['name']]
                        ),
                        TermAction(
                            text = "Remove",
                            commandline = ["composer", "global", "remove", package['name']]
                        )
                    ]
                )
            )

    return items
