# -*- coding: utf-8 -*-

"""Sets default audio sink

 Synopsis: <trigger> <query>"""

import subprocess
from albert import *

__title__ = "Pulseaudio cmd"
__version__ = "0.1.0"
__triggers__ = "pacmd "
__authors__ = "c4pQ"
__exec_deps__ = ['pacmd']

iconPath = iconLookup('audio-headphones')

def buildActions():
    pacmd_actions = []
    pacmd_output = subprocess.check_output(['pacmd', 'list-sinks']).splitlines()
    sinks = [l[len('\t\tdevice.description = '):].decode() for l in pacmd_output if 'device.description' in str(l)]
    for sink, i in zip(sinks, range(1, len(sinks) + 1)):
        cl = ['pacmd', 'set-default-sink', str(i)]
        pacmd_actions.append([i, sink, ProcAction(text=f'Set {sink} default', commandline=cl)])
    return pacmd_actions

def handleQuery(query):
    items = []
    if query.isValid and query.isTriggered:
        actions = buildActions()
        for action in actions:
            items.append(Item(
                id=f'pacmd-set-sink-{action[0]}',
                icon=iconPath,
                text=action[1],
                subtext=f'Make {action[1]} default audio sink',
                completion=action[1],
                actions=[ action[2] ]
            ))
    return items
