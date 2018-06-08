# -*- coding: utf-8 -*-

"""List and open your Atom projects"""

import os
import re
import time
from pathlib import Path
from shutil import which

import cson

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Atom Projects"
__version__ = "1.0"
__trigger__ = "atom "
__author__ = "Manuel Schneider"
__dependencies__ = ["python-cson"]

projects_file = str(Path.home()) + "/.atom/projects.cson"

if which("atom") is None:
    raise Exception("'atom' is not in $PATH.")

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
            items.append(Item(id=__prettyname__ + project['title'],
                              icon=iconPath,
                              text=project['title'],
                              subtext="Group: %s" % (project['group'] if 'group' in project else "None"),
                              completion=query.rawString,
                              actions=[
                                  ProcAction(text="Open project in Atom",
                                             commandline=["atom"] + project['paths'])
                              ]))
    return items
