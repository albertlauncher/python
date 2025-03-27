# -*- coding: utf-8 -*-
# Copyright (c) 2022 Manuel Schneider
# Copyright (c) 2022 Benedict Dudel
# Copyright (c) 2022 Pete Hamlin


import os
from signal import SIGKILL, SIGTERM

from albert import *

md_iid = "3.0"
md_version = "2.0"
md_name = "Kill Process"
md_description = "Kill processes"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/kill"
md_authors = ["@Pete-Hamlin", "@BenedictDwudel", "@ManuelSchneid3r"]


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

    def defaultTrigger(self):
        return "kill "

    def handleTriggerQuery(self, query):
        if not query.isValid:
            return
        results = []
        uid = os.getuid()
        for dir_entry in os.scandir("/proc"):
            try:
                if dir_entry.name.isdigit() and dir_entry.stat().st_uid == uid:
                    proc_command = (
                        open(os.path.join(dir_entry.path, "comm"), "r").read().strip()
                    )
                    if query.string in proc_command:
                        debug(proc_command)
                        proc_cmdline = (
                            open(os.path.join(dir_entry.path, "cmdline"), "r")
                            .read()
                            .strip()
                            .replace("\0", " ")
                        )
                        results.append(
                            StandardItem(
                                id="kill",
                                iconUrls=["xdg:process-stop"],
                                text=proc_command,
                                subtext=proc_cmdline,
                                actions=[
                                    Action(
                                        "terminate",
                                        "Terminate process",
                                        lambda pid=int(dir_entry.name): os.kill(
                                            pid, SIGTERM
                                        ),
                                    ),
                                    Action(
                                        "kill",
                                        "Kill process",
                                        lambda pid=int(dir_entry.name): os.kill(
                                            pid, SIGKILL
                                        ),
                                    ),
                                ],
                            )
                        )
            except FileNotFoundError:  # TOCTOU dirs may disappear
                continue
            except IOError:  # TOCTOU dirs may disappear
                continue
        query.add(results)
