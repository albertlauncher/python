# -*- coding: utf-8 -*-

"""List and manage X11 windows.

Synopsis: <filter>"""

import subprocess
from collections import namedtuple
from shutil import which

from albert import Item, ProcAction, iconLookup

Window = namedtuple("Window", ["wid", "desktop", "wm_class", "host", "wm_name"])

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Window Switcher"
__version__ = "1.5"
__author__ = "Ed Perez, manuelschneid3r, dshoreman"
__dependencies__ = ["wmctrl"]

if which("wmctrl") is None:
    raise Exception("'wmctrl' is not in $PATH.")

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
                iconPath = iconLookup(win_instance)
                if iconPath == "":
                    iconPath = iconLookup(win_class.lower())

                results.append(Item(id="%s%s" % (__prettyname__, win.wm_class),
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
