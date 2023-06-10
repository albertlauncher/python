# -*- coding: utf-8 -*-

"""List and open your Atom projects.

Synopsis: <trigger> [filter]"""

#  Copyright (c) 2022 Manuel Schneider

import os
import re
import time
from pathlib import Path

import cson

from albert import *

__title__ = "Atom Projects"
__version__ = "0.4.0"
__triggers__ = "atom "
__authors__ = "Manuel S."
__exec_deps__ = ["atom"]
__py_deps__ = ["cson"]

projects_file = str(Path.home()) + "/.atom/projects.cson"
iconPath = iconLookup('atom')
mtime = 0
projects = []


def updateProjects():
    global mtime
    try:
        new_mtime = os.path.getmtime(projects_file)
    except Exception as e:
        warning("Could not get mtime of file: " + projects_file + str(e))
    if mtime != new_mtime:
        mtime = new_mtime
        with open(projects_file) as projects_cson:
            global projects
            projects = cson.loads(projects_cson.read())


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
                              subtext="Group: %s" % (project['group'] if 'group' in project else "None"),
                              actions=[
                                  ProcAction(text="Open project in Atom",
                                             commandline=["atom"] + project['paths'])
                              ]))
    return items
