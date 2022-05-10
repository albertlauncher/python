# -*- coding: utf-8 -*-

"""

"""


import os
import re
import json
import sqlite3
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
storage_db = str(Path.home()) + "/.config/Code/User/globalStorage/state.vscdb"

iconPath = iconLookup("visual-studio-code")
mtime = 0
projects = []


def get_vscode_project():
    conn = sqlite3.connect(storage_db)
    cur = conn.cursor()
    try:
        df = cur.execute("select value from ItemTable where key='history.recentlyOpenedPathsList'")  # noqa
        row = cur.fetchone()
        entries = json.loads(row[0])['entries']
    except KeyError:
        pass
    finally:
        cur.close()
        conn.close()

    result = []
    for entry in entries:
        if 'folderUri' in entry:
            uri = entry['folderUri']
            title = os.path.basename(uri)
            print(entry)
            if uri.startswith("vscode-remote://"):
                title = "remote: {}".format(title)
            if uri.startswith("file://"):
                if not os.path.isdir(uri[7:]):
                    continue
            result.append({
                'title': title,
                'paths': [uri],
            })
    return result


def updateProjects():
    global mtime
    try:
        new_mtime = os.path.getmtime(storage_db)
    except Exception as e:
        warning("Could not get mtime of file: " + storage_file + str(e))
    if mtime != new_mtime:
        mtime = new_mtime
        projects = get_vscode_project()


def handleQuery(query):
    if not query.isTriggered:
        return

    # updateProjects()

    stripped = query.string.strip()

    items = []
    for project in get_vscode_project():
        if re.search(stripped, project['title'], re.IGNORECASE):
            items.append(Item(id=__title__ + project['title'],
                              icon=iconPath,
                              text=project['title'],
                              subtext="Path: %s" % (project['paths']),
                              actions=[
                                  ProcAction(text="Open project in VSCode",
                                             commandline=["code"] + ["--folder-uri"] + project['paths'])  # noqa
                              ]))
    return items


def main():
    get_vscode_project()


if __name__ == "__main__":
    main()
