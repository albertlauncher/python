import os
from shutil import which
from xml.etree import ElementTree
from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Jetbrains IDE Projects"
__version__ = "1.0"
__trigger__ = "jb "
__author__ = "Markus Richter"
__dependencies__ = []

paths = [#<Name for config directory>, <possible names for the binary>, <possible names of the .desktop file>
    ["CLion", "clion", "jetbrains-clion"],
    ["DataGrip", "datagrip", "jetbrains-datagrip"],
    ["GoLand", "goland", "jetbrains-goland"],
    ["IntelliJIdea", "intellij-idea-ue-bundled-jre intellij-idea-ultimate-edition idea-ce-eap idea-ue-eap",
     "jetbrains-idea"],
    ["PhpStorm", "phpstorm", "jetbrains-phpstorm"],
    ["PyCharm", "pycharm pycharm-eap charm", "jetbrains-pycharm"],
    ["WebStorm", "webstorm", "jetbrains-webstorm"],
]

#find the executable path and icon of a program described by space-separated lists of possible binary-names / .desktop-file names
def find_exec(namestr: str, dnamestr: str):
    binpath = None
    for name in namestr.split(" "):
        s = which(name)
        if s is not None:
            binpath = s
            break

    if binpath is None:
        return None
    for dname in dnamestr.split(" "):
        s = iconLookup(name)
        if s is not None:
            return (binpath, s)

    return None


HOME_DIR = os.environ["HOME"]


#parse the xml at path, return all recent project paths and the time they were last open
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
            configpath = "config/options/recentProjectDirectories.xml"
            if app[0] == "IntelliJIdea":
                configpath = "config/options/recentProjects.xml"
            
            #dirs contains possibly multiple directories for a program (eg. .GoLand2018.1 and .GoLand2017.3). take the newest.
            dirs = [f for f in os.listdir(HOME_DIR) if
                    os.path.isdir(os.path.join(HOME_DIR, f)) and f.startswith("." + app[0])]
            dirs.sort(reverse=True)
            if len(dirs) == 0:
                continue
            configpath = os.path.join(HOME_DIR, dirs[0], configpath)

            #extract the binary name and icon
            binaries[app[0]] = find_exec(app[1], app[2])

            #add all recently opened projects
            projects.extend([[e[0], e[1], app[0]] for e in get_proj(configpath)])
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
