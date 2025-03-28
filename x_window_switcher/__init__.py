# -*- coding: utf-8 -*-

import subprocess
from collections import namedtuple
from albert import *

md_iid = "3.0"
md_version = "0.6.0"
md_name = "X Window Switcher"
md_description = "Switch X11 Windows"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/x_window_switcher"
md_bin_dependencies = "wmctrl"
md_authors = ["Ed Perez", "Manuel S.", "dshoreman", "nopsqi"]

Window = namedtuple("Window", ["wid", "desktop", "wm_class", "host", "wm_name"])


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

        # Check for X session and wmctrl availability
        try:
            subprocess.check_call(["wmctrl", "-m"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            raise Exception("wmctrl not found. Please install wmctrl.")
        except subprocess.CalledProcessError:
            raise Exception("Unable to communicate with X11 window manager. This plugin requires a running X session.")

    def defaultTrigger(self):
        return 'w '

    def handleTriggerQuery(self, query):
        try:
            for line in subprocess.check_output(['wmctrl', '-l', '-x']).splitlines():
                win = Window(*parseWindow(line))

                if win.desktop == "-1":
                    continue

                win_instance, win_class = win.wm_class.replace(' ', '-').split('.', 1)

                m = Matcher(query.string)
                if not query.string or m.match(win_instance + ' ' + win_class + ' ' + win.wm_name):
                    query.add(StandardItem(
                        id="%s%s" % (md_name, win.wm_class),
                        iconUrls=["xdg:%s" % win_instance],
                        text="%s  - Desktop %s" % (win_class.replace('-', ' '), win.desktop),
                        subtext=win.wm_name,
                        actions=[Action("switch",
                                        "Switch Window",
                                        lambda w=win: runDetachedProcess(["wmctrl", '-i', '-a', w.wid])),
                                Action("move",
                                        "Move window to this desktop",
                                        lambda w=win: runDetachedProcess(["wmctrl", '-i', '-R', w.wid])),
                                Action("close",
                                        "Close the window gracefully.",
                                        lambda w=win: runDetachedProcess(["wmctrl", '-c', w.wid]))]
                    ))
        except subprocess.CalledProcessError as e:
            warning(f"Error executing wmctrl: {str(e)}")


def parseWindow(line):
    win_id, desktop, rest = line.decode().split(None, 2)
    win_class, rest = rest.split('  ', 1)
    host, title = rest.strip().split(None, 1)

    return [win_id, desktop, win_class, host, title]
