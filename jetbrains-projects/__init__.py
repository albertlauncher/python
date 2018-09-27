# -*- coding: utf-8 -*-

"""List and open JetBrains IDE projects."""

import os
from shutil import which
from xml.etree import ElementTree

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Jetbrains IDE Projects"
__version__ = "1.1"
__trigger__ = "jb "
__author__ = "Markus Richter, Thomas Queste"
__dependencies__ = []

default_icon = os.path.dirname(__file__) + "/jetbrains.svg"
HOME_DIR = os.environ["HOME"]

paths = [  # <Name for config directory>, <possible names for the binary/icon>
    ["CLion", "clion"],
    ["DataGrip", "datagrip"],
    ["GoLand", "goland"],
    ["IntelliJIdea",
     "intellij-idea-ue-bundled-jre intellij-idea-ultimate-edition idea-ce-eap idea-ue-eap idea idea-ultimate"],
    ["PhpStorm", "phpstorm"],
    ["PyCharm", "pycharm pycharm-eap charm"],
    ["WebStorm", "webstorm"],
]


# find the executable path and icon of a program described by space-separated lists of possible binary-names
def find_exec(namestr: str):
    for name in namestr.split(" "):
        executable = which(name)
        if executable:
            icon = iconLookup(name) or default_icon
            return executable, icon
    return None


# parse the xml at path, return all recent project paths and the time they were last open
def get_proj(path):
    r = ElementTree.parse(path).getroot()  # type:ElementTree.Element
    add_info = None
    items = dict()
    for o in r[0]:  # type:ElementTree.Element
        if o.attrib["name"] == 'recentPaths':
            for i in o[0]:
                items[i.attrib["value"]] = 0

        else:
            if o.attrib["name"] == 'additionalInfo':
                add_info = o[0]

    if len(items) == 0:
        return []

    if add_info is not None:
        for i in add_info:
            for o in i[0][0]:
                if o.attrib["name"] == 'projectOpenTimestamp':
                    items[i.attrib["key"]] = int(o.attrib["value"])
    return [(items[e], e.replace("$USER_HOME$", HOME_DIR)) for e in items]


def handleQuery(query):
    if query.isTriggered or query.string is not "":
        binaries = {}
        projects = []

        for app in paths:
            config_path = "config/options/recentProjectDirectories.xml"
            if app[0] == "IntelliJIdea":
                config_path = "config/options/recentProjects.xml"

            # dirs contains possibly multiple directories for a program (eg. .GoLand2018.1 and .GoLand2017.3)
            dirs = [f for f in os.listdir(HOME_DIR) if
                    os.path.isdir(os.path.join(HOME_DIR, f)) and f.startswith("." + app[0])]
            # take the newest
            dirs.sort(reverse=True)
            if len(dirs) == 0:
                continue

            config_path = os.path.join(HOME_DIR, dirs[0], config_path)
            if not os.path.exists(config_path):
                continue

            # extract the binary name and icon
            binaries[app[0]] = find_exec(app[1])

            # add all recently opened projects
            projects.extend([[e[0], e[1], app[0]] for e in get_proj(config_path)])
        projects.sort(key=lambda s: s[0], reverse=True)
        return [Item(
            id="-" + str(p[0]),
            icon=binaries[p[2]][1],
            text=p[1].split("/")[-1],
            subtext=p[1],
            completion=__trigger__ + p[1].split("/")[-1],
            actions=[
                ProcAction("Open in %s" % p[2], [binaries[p[2]][0], p[1]])
            ]
        ) for p in projects if p[1].lower().find(query.string.lower()) != -1]
