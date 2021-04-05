# -*- coding: utf-8 -*-

"""List and manage X11 windows.

Synopsis: <filter>"""

import subprocess
from collections import namedtuple
from albert import Item, ProcAction, iconLookup

__title__ = "Window Switcher"
__version__ = "0.4.5"
__authors__ = ["Ed Perez", "manuelschneid3r", "dshoreman"]
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

            # Usually the WM_CLASS output from wmctrl consists of instance and
            # class name separated by a dot. In some cases, the instance and
            # class name can dontain a dot themselves (e.g. org.gnome.Nautilus).
            # In that case we assume that both parts have the same number of
            # pieces and split them in the middle.
            win_instance = win.wm_class
            win_class = ""

            wm_class_pieces = win.wm_class.replace(' ', '-').split('.')
            if len(wm_class_pieces) % 2 == 0:
                win_insthutance = '.'.join(wm_class_pieces[:len(wm_class_pieces) // 2])
                win_class = '.'.join(wm_class_pieces[len(wm_class_pieces) // 2:])

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
