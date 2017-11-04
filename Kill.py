""" Kill Process Extension """

import os
import getpass
from albertv0 import *
from subprocess import Popen, PIPE

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Kill Process"
__version__ = "1.0"
__trigger__ = "kill "
__author__ = "Benedict Dudel"
__dependencies__ = []

iconPath = iconLookup('process-stop')

def handleQuery(query):
    if query.isTriggered:
        results = []
        for process in getProcesses(query.string.strip()):
            results.append(
                Item(
                    id=process['id'],
                    icon=iconPath,
                    text=process['name'],
                    subtext="CPU: %s %%" % process['cpu'],
                    completion="",
                    actions=[
                        ProcAction(
                            "Request termination",
                            ["kill", "-SIGTERM", process['id']]
                        ),
                        ProcAction(
                            "Terminate immediately",
                            ["kill", "-SIGKILL", process['id']]
                        ),
                    ]
                )
            )

        return results

def getProcesses(searchString):
    process = Popen(
        ['ps', '-o' ,'pid,comm,%cpu', '-u', getpass.getuser()],
        stdout=PIPE, stderr=PIPE
    )
    stdout, notused = process.communicate()

    processes = []
    for line in stdout.splitlines():
        columns = line.split()

        id = str(columns[0], 'utf-8')
        if not id:
            continue

        name = str(columns[1], 'utf-8')
        if not name:
            continue

        cpu = str(columns[2], 'utf-8')
        if not cpu:
            cpu = "0.0"

        if searchString and searchString not in name:
            continue

        processes.append({'id': id, 'name': name, 'cpu': cpu})

    return processes
