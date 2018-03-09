"""locate adapter extension

Note that it is up to you to ensure that the database is up to date"""

import os
import subprocess
from shutil import which
from albertv0 import *
import re

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Apt"
__version__ = "1.0"
__trigger__ = "apt"
__author__ = "Harindu Dilshan"
__dependencies__ = ['apt','gksu','pkexec']

if which("apt") is None:
    raise Exception("'Apt' is not in $PATH.")

gksu = None
for item in __dependencies__:
    if which(item):
        gksu = item

UpdateActions = [TermAction("Update database in Terminal", ["sudo", "apt", "update"])]

if gksu is not None:
    UpdateActions.insert(0,FuncAction("Update database",lambda :subprocess.Popen([gksu,"apt","update"])))

iconPath = iconLookup("system-software-install")

def handleQuery(query):
    results = []
    if query.isTriggered:
        if len(query.string) > 2:
            # pattern = re.compile(query.string, re.IGNORECASE)
            shell_cmd = ["apt-cache" ,"search"]
            pattern = query.string.split(" ")
            proc = subprocess.Popen(shell_cmd + pattern, stdout=subprocess.PIPE)
            for line in proc.stdout:
                path = line.decode().strip()
                index = path.index(" - ")
                name = path[:index]
                description = path[index+3:]
                results.append(
                    Item(
                        id=line,
                        icon=iconPath,
                        text=name,
                        subtext=description,
                        completion="%s%s" % (__trigger__, query.string),
                        actions=[TermAction("Install " + name, ["sudo","apt","install",name]),
                        TermAction("Remove " + name, ["sudo","apt","remove",name])]))
        else:
            results.append(
                Item(
                    id=__prettyname__,
                    icon=iconPath,
                    text="Update apt database",
                    subtext="Type at least three chars for a seach",
                    completion=query.rawString,
                    actions=UpdateActions))

    return results

