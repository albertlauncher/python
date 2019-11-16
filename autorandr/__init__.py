# -*- coding: utf-8 -*-

"""Load and save autorandr configs.

Load and save  configs. Requires autorandr to be installed.

Synopsis: <trigger> [load|save] <config>"""

from albertv0 import *
import os
import subprocess
from time import sleep


__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Autorandr"
__version__ = "1.0"
__trigger__ = "ar "
__author__ = "Rhys Tyers"
__dependencies__ = ["autorandr"]

configurations = []

def initialize():
    global configurations
    result = subprocess.run(["autorandr", "--detected"], stdout=subprocess.PIPE)
    result.stdout.decode('utf-8')
    configurations = result.stdout.decode().split()

def handleQuery(query):
    if not query.isTriggered:
        return

    queryList = query.string.split()
    results = []

    # Load
    if queryList[0] != 'load' and 'load'.startswith(queryList[0]):
        item = Item(id=__prettyname__,
                    icon=os.path.dirname(__file__)+"/monitor.svg",
                    text="Load",
                    subtext="Load a saved xrandr configuration",
                    completion=__trigger__ + 'load ',
                    urgency=ItemBase.Alert,
                    actions=[])
        results.append(item)
    if queryList[0] == 'load':
        for configuration in configurations:
            if len(queryList) < 2 or configuration.startswith(queryList[1]):
                item = Item(id=__prettyname__,
                            icon=os.path.dirname(__file__)+"/monitor.svg",
                            text="Load " + configuration,
                            subtext="Load the " + configuration + " xrandr configuration",
                            completion=__trigger__ + 'load ' + configuration,
                            urgency=ItemBase.Alert,
                            actions=[
                                ProcAction(text="ProcAction",
                                        commandline=["autorandr", "--change", configuration],
                                        )
                            ])
                results.append(item)
    
    # Save
    if queryList[0] != 'save' and 'save'.startswith(queryList[0]):
        item = Item(id=__prettyname__,
                    icon=os.path.dirname(__file__)+"/monitor.svg",
                    text="Save",
                    subtext="Save the current xrandr configuration",
                    completion=__trigger__ + 'save ',
                    urgency=ItemBase.Alert,
                    actions=[])
        results.append(item)
    if queryList[0] == 'save':
        item = Item(id=__prettyname__,
                    icon=os.path.dirname(__file__)+"/monitor.svg",
                    text="Save " + queryList[1],
                    subtext="Save the current xrandr configuration as " + queryList[1],
                    urgency=ItemBase.Alert,
                    completion=__trigger__ + 'save ',
                    actions=[
                        ProcAction(text="ProcAction",
                                commandline=["autorandr", "--save", queryList[1]],
                                )
                    ])
        results.append(item)

    return results
