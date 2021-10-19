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

            # Normal wm_classes have a single dot separating the instance and
            # the class and the better window name to display during matching
            # is the class (e.g. "Navigator.Firefox").
            #
            # Some wm_classes have no dots (e.g "N/A" for Chrome's Ozone X11
            # process) and should be skipped.
            #
            # Some wm_classes have more than one, such as under Wine (e.g.
            # "rufus-3.17.exe.rufus-3.17.exe"). In this case, a decent
            # heuristic is to use the text before the first dot to display.

            clean_wm_class = win.wm_class.replace(' ', '-')
            dots_in_wm_class = clean_wm_class.count('.')

            if dots_in_wm_class == 0:
                continue

            win_instance, win_class = clean_wm_class.split('.', 1)
            win_display = win_class

            if dots_in_wm_class > 1:
                win_display = win_instance

            matches = [
                win_instance.lower(),
                win_class.lower(),
                win.wm_name.lower()
            ]

            if any(stripped in match for match in matches):
                iconPath = iconLookup(win_instance) or iconLookup(win_class.lower())
                results.append(Item(id="%s%s" % (__title__, win.wm_class),
                                    icon=iconPath,
                                    text="%s  - <i>Desktop %s</i>" % (win_display.replace('-',' '), win.desktop),
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
