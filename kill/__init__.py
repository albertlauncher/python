# -*- coding: utf-8 -*-

"""Kill processes.

Unix 'kill' wrapper extension.

Synopsis: <trigger> <filter>"""

import os
from signal import SIGKILL, SIGTERM

from albert import FuncAction, Item, iconLookup

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Kill Process"
__version__ = "1.4"
__trigger__ = "kill "
__author__ = "Benedict Dudel, Manuel Schneider"
__dependencies__ = []

iconPath = iconLookup('process-stop')


def handleQuery(query):
    if query.isTriggered:
        results = []
        uid = os.getuid()
        for dir_entry in os.scandir('/proc'):
            try:
                if dir_entry.name.isdigit() and dir_entry.stat().st_uid == uid:
                    proc_command = open(os.path.join(dir_entry.path, 'comm'), 'r').read().strip()
                    if query.string in proc_command:
                        proc_cmdline = open(os.path.join(dir_entry.path, 'cmdline'), 'r').read().strip().replace("\0", " ")
                        results.append(
                            Item(
                                id="kill_%s" % proc_cmdline,
                                icon=iconPath,
                                text=proc_command.replace(query.string, "<u>%s</u>" % query.string),
                                subtext=proc_cmdline,
                                completion=query.rawString,
                                actions=[
                                    FuncAction("Terminate", lambda pid=int(dir_entry.name): os.kill(pid, SIGTERM)),
                                    FuncAction("Kill", lambda pid=int(dir_entry.name): os.kill(pid, SIGKILL))
                                ]
                            )
                        )
            except FileNotFoundError:  # TOCTOU dirs may disappear
                continue
            except IOError:  # TOCTOU dirs may disappear
                continue
        return results
