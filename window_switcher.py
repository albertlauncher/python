# -*- coding: utf-8 -*-

"""List and manage X11 windows.

Synopsis: <filter>"""

import subprocess
from collections import namedtuple
from shutil import which

from albertv0 import Item, ProcAction, iconLookup

Window = namedtuple("Window", ["wid", "desktop", "wm_class", "host", "wm_name"])

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Window Switcher"
__version__ = "1.5"
__author__ = "Ed Perez, Manuel Schneider"
__dependencies__ = ["wmctrl"]

if which("wmctrl") is None:
    raise Exception("'wmctrl' is not in $PATH.")

def matchWindow(win, text):
    return (text in win.wm_class.lower() or text in win.wm_name.lower())

def handleQuery(query):
    stripped = query.string.strip().lower().split()
    if stripped:
        results = []
        for line in subprocess.check_output(['wmctrl', '-l', '-x']).splitlines():
            win = Window(*[token.decode() for token in line.split(None,4)])
            if win.desktop != "-1" and all(matchWindow(win, text) for text in stripped):
                results.append(Item(id="%s%s" % (__prettyname__, win.wm_class),
                                    icon=iconLookup(win.wm_class.split('.')[0]),
                                    text="%s  - <i>Desktop %s</i>" % (win.wm_class.split('.')[-1].replace('-',' '), win.desktop),
                                    subtext=win.wm_name,
                                    actions=[ProcAction("Switch Window",
                                                        ["wmctrl", '-i', '-a', win.wid] ),
                                             ProcAction("Move window to this desktop",
                                                        ["wmctrl", '-i', '-R', win.wid] ),
                                             ProcAction("Close the window gracefully.",
                                                        ["wmctrl", '-c', win.wid])]))
        return results
