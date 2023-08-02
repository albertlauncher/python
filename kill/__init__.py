"""Unix 'kill' wrapper extension."""

import os
from signal import SIGKILL, SIGTERM

from albert import *

md_iid = '2.0'
md_version = "1.3"
md_name = "Kill Process"
md_description = "Kill processes"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/kill"
md_maintainers = "@Pete-Hamlin"
md_credits = "Original idea by Benedict Dudel & Manuel Schneider"


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     defaultTrigger='kill ')
        PluginInstance.__init__(self, extensions=[self])

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
