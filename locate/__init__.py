# -*- coding: utf-8 -*-

"""Find and open files.

Unix 'locate' wrapper extension. Note that it is up to you to ensure that the locate database is \
up to date.

This extensions is intended as secondary way to find files. Use the files extension for often used \
files and fast lookups and this extension for everything else.

Synopsis: <trigger> [filter]"""

import os
import re
import subprocess

from albert import Item, TermAction, UrlAction, iconLookup, warning

__title__ = "Locate"
__version__ = "0.4.0"
__triggers__ = "'"
__authors__ = "manuelschneid3r"
__exec_deps__ = ['locate']

iconPath = iconLookup(["preferences-system-search", "system-search" "search", "text-x-generic"])

def handleQuery(query):
    results = []
    if query.isTriggered:
        if len(query.string) > 2:
            pattern = re.compile(query.string, re.IGNORECASE)
            proc = subprocess.Popen(['locate', '-i', query.string], stdout=subprocess.PIPE)
            for line in proc.stdout:
                path = line.decode().strip()
                basename = os.path.basename(path)
                results.append(
                    Item(
                        id=path,
                        icon=iconPath,
                        text=pattern.sub(lambda m: "<u>%s</u>" % m.group(0), basename),
                        subtext=path,
                        completion="%s%s" % (__triggers__, basename),
                        actions=[UrlAction("Open", "file://%s" % path)]))
        else:
            results.append(
                Item(
                    id=__title__,
                    icon=iconPath,
                    text="Update locate database",
                    subtext="Type at least three chars for a seach",
                    actions=[TermAction("Update database", ["sudo", "updatedb"])]))

    return results
