# -*- coding: utf-8 -*-

"""Remmina extension.

Connect to your Remmina thingies.."""

from albertv0 import FuncAction, Item, critical, iconLookup, info
import os
from subprocess import call

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Remmina"
__version__ = "1.0"
__trigger__ = "remm "
__author__ = "Max Ried"
__dependencies__ = []

REMMINA_DIR = os.getenv('HOME') + '/.local/share/remmina/'

for iconName in ["org.remmina.Remmina", "unknown"]:
    iconPath = iconLookup(iconName)
    if iconPath:
        break

def initialize():
    pass

def finalize():
    pass

def connectionFiles():
    files = []

    for f in os.listdir(REMMINA_DIR):
        if f.endswith(".remmina"):
            files.append(f)

    return files

def remminaEdit(file):
    os.system('remmina --edit=' + file)
#    call(['remmina', '--edit="{file}"'.format(file=file)])

def remminaConnect(file):
    os.system('remmina --connect=' + file)
#    call(['remmina', '--connect="{file}"'.format(file=file)])

def buildItems(file):
    name = None
    protocol = None
    username = None
    server = None

    path = REMMINA_DIR + file

    with open(path, mode='rt') as s:
        for currentLine in s.readlines():
            currentLine = currentLine.strip()
            if currentLine.startswith('name='):
                name = currentLine[5:]
            elif currentLine.startswith('protocol='):
                protocol = currentLine[9:]
            elif currentLine.startswith('username='):
                username = currentLine[9:]
            elif currentLine.startswith('server='):
                server = currentLine[7:]
        

    item = None

    if name is not None and protocol is not None:
        item = Item(id=os.path.basename(file),
                     text=name,
                     icon=iconPath,
                     subtext='{name} ({userpart}{server} via {protocol})'
                        .format(name=name, userpart=(username + '@' if username != '' else ''), server=server, protocol=protocol),
                     completion=name)

        item.addAction(FuncAction(text='Connect', callable=lambda: remminaConnect(path)))
        item.addAction(FuncAction(text='Edit connection', callable=lambda: remminaEdit(path)))

    return item

def handleQuery(query):
    pattern = query.string.strip().lower()
    results = []
    
    for f in connectionFiles():
        result = buildItems(f)
        if result is not None:
            if (pattern and pattern in result.completion.lower() or not pattern and query.isTriggered):
                results.append(result)
    
    return results
