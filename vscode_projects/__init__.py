# -*- coding: utf-8 -*-

"""

"""


import os
import re
import json
from pathlib import Path

try:
    from albert import *
except Exception as e:
    def info(v):
        return print(v)

    def iconLookup(v):
        pass

__title__ = "VSCode Projects"
__version__ = "0.1.0"
__triggers__ = "&c"
__authors__ = "corvofeng"
__exec_deps__ = ['code']


storage_file = str(Path.home()) + "/.config/Code/storage.json"
iconPath = iconLookup("visual-studio-code")
mtime = 0
projects = []


def get_vscode_project(storage_json):
    storage_dict = json.loads(storage_json)
    entries = storage_dict['openedPathsList']['entries']
    result = []
    for entry in entries:
        if 'folderUri' in entry:
            uri = entry['folderUri']
            title = os.path.basename(uri)
            if uri.startswith("vscode-remote://"):
                title = "remote: {}".format(title)
            result.append({
                'title': title,
                'paths': [uri],
            })
    return result


def updateProjects():
    global mtime
    try:
        new_mtime = os.path.getmtime(storage_file)
    except Exception as e:
        warning("Could not get mtime of file: " + storage_file + str(e))
    if mtime != new_mtime:
        mtime = new_mtime
        with open(storage_file) as f:
            global projects
            projects = get_vscode_project(f.read())


def handleQuery(query):
    if not query.isTriggered:
        return

    updateProjects()

    stripped = query.string.strip()

    items = []
    for project in projects:
        if re.search(stripped, project['title'], re.IGNORECASE):
            items.append(Item(id=__title__ + project['title'],
                              icon=iconPath,
                              text=project['title'],
                              subtext="Path: %s" % (project['paths']),
                              actions=[
                                  ProcAction(text="Open project in VSCode",
                                             commandline=["code"] + ["--folder-uri"] + project['paths'])
                              ]))
    return items


def main():
    with open(storage_file) as f:
        print(get_vscode_project(f.read()))


if __name__ == "__main__":
    main()