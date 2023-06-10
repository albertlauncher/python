# -*- coding: utf-8 -*-

"""List and manage X11 windows.

Synopsis: <filter>"""

#  Copyright (c) 2022 Manuel Schneider

import subprocess
from collections import namedtuple
from albert import Item, ProcAction, iconLookup

__title__ = "Window Switcher"
__version__ = "0.4.5"
__authors__ = ["Ed Perez", "Manuel S.", "dshoreman"]
__exec_deps__ = ["wmctrl"]

Window = namedtuple("Window", ["wid", "desktop", "wm_class", "host", "wm_name"])

def handleQuery(query):
    stripped = query.string.strip().lower()
    if stripped:
        results = []
        for line in subprocess.check_output(['wmctrl', '-l', '-x']).splitlines():
            win = Window(*parseWindow(line))

            if win.desktop == "-1":
                continue

            win_instance, win_class = win.wm_class.replace(' ', '-').split('.')
            matches = [
                win_instance.lower(),
                win_class.lower(),
                win.wm_name.lower()
            ]

            if any(stripped in match for match in matches):
                iconPath = iconLookup(win_instance) or iconLookup(win_class.lower())
                results.append(Item(id="%s%s" % (__title__, win.wm_class),
                                    icon=iconPath,
                                    text="%s  - <i>Desktop %s</i>" % (win_class.replace('-',' '), win.desktop),
                                    subtext=win.wm_name,
                                    actions=[ProcAction("Switch Window",
                                                        ["wmctrl", '-i', '-a', win.wid] ),
                                             ProcAction("Move window to this desktop",
                                                        ["wmctrl", '-i', '-R', win.wid] ),
                                             ProcAction("Close the window gracefully.",
                                                        ["wmctrl", '-c', win.wid])]))
        return results

def parseWindow(line):
    win_id, desktop, rest = line.decode().split(None, 2)
    win_class, rest = rest.split('  ', 1)
    host, title = rest.strip().split(None, 1)

    return [win_id, desktop, win_class, host, title]
