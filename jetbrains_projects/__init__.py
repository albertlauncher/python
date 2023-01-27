# -*- coding: utf-8 -*-

"""List and open JetBrains IDE projects."""

import os
import time
from shutil import which
from xml.etree import ElementTree

from albert import *

md_iid = "0.5"
md_version = "0.5"
md_name = "Jetbrains"
md_description = "Open Jetbrains IDE projects"
md_license = "GPL-3"
md_url = "https://github.com/mqus/jetbrains-albert-plugin"
md_maintainers = ["@mqus", "@tomsquest"]
md_authors = "@mqus"

default_icon = os.path.dirname(__file__) + "/jetbrains.svg"
HOME_DIR = os.environ["HOME"]

JETBRAINS_XDG_CONFIG_DIR = os.path.join(HOME_DIR, ".config/JetBrains")
GOOGLE_XDG_CONFIG_DIR = os.path.join(HOME_DIR, ".config/Google")

# for all new (2020.1+) config folders and IntelliJIdea and AndroidStudio, this is the right path.
NEW_RELATIVE_CONFIG_PATH = "options/recentProjects.xml"
# for older config folders of other IDEs, the following is right:
OLD_RELATIVE_CONFIG_PATH = "options/recentProjectDirectories.xml"

# <Name for config directory>, <possible names for the binary/icon>
paths = [
    ["AndroidStudio", "android-studio"],
    ["CLion", "clion"],
    ["DataGrip", "datagrip"],
    ["GoLand", "goland"],
    ["IntelliJIdea", "intellij-idea-ue-bundled-jre intellij-idea-ultimate-edition idea-ce-eap idea-ue-eap idea idea-ultimate"],
    ["PhpStorm", "phpstorm"],
    ["PyCharm", "pycharm pycharm-eap charm"],
    ["RubyMine", "rubymine jetbrains-rubymine jetbrains-rubymine-eap"],
    ["WebStorm", "webstorm"],
]


class Plugin(QueryHandler):
    def id(self):
        return __name__

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "jb "

    def initialize(self):
        pass

    def handleQuery(self, query: Query):
        # a dict which maps the app name to a tuple of executable path and icon.
        binaries = {}
        # an array of tuples representing the project([timestamp,path,app name])
        projects = []

        for app in paths:
            # get configuration file path
            full_config_path = self.find_config_path(app[0])

            if full_config_path is None:
                continue

            # extract the binary name and icon
            binaries[app[0]] = self.find_exec(app[1])

            # add all recently opened projects
            projects.extend(
                [[e[0], e[1], app[0]] for e in self.get_proj(full_config_path)]
            )

        # List all projects or the one corresponding to the query
        if query.string:
            projects = [
                p for p in projects if p[1].lower().find(query.string.lower()) != -1
            ]

        # sort by last modified, most recent first.
        projects.sort(key=lambda p: p[0], reverse=True)

        items = []
        now = int(time.time() * 1000.0)
        for p in projects:
            last_update = p[0]
            project_path = p[1]
            if not os.path.exists(project_path):
                continue
            project_dir = project_path.split("/")[-1]
            app_name = p[2]
            binary = binaries[app_name]
            if not binary:
                continue

            executable = binary[0]
            icon = binary[1]

            items.append(
                Item(
                    id="%015d-%s-%s" % (now - last_update, project_path, app_name),
                    text=project_dir,
                    subtext="Open %s with %s" % (project_path, app_name),
                    completion=query.trigger + project_dir,
                    icon=[icon, default_icon],
                    actions=[
                        Action(
                            "Open",
                            "Open in %s" % app_name,
                            lambda selected_project=project_path: runDetachedProcess(
                                [executable, selected_project]
                            ),
                        )
                    ],
                )
            )

        query.add(items)

    # find the executable path and icon of a program described by space-separated lists of possible binary-names
    def find_exec(self, namestr: str):
        for name in namestr.split(" "):
            executable = which(name)
            if executable:
                return executable, "xdg:%s" % name
        else:
            return None

    # parse the xml at path, return all recent project paths and the time they were last open
    def get_proj(self, path: str):
        root = ElementTree.parse(path).getroot()  # type:ElementTree.Element
        add_info = None
        path2timestamp = dict()
        for option_tag in root[0]:  # type:ElementTree.Element
            if option_tag.attrib["name"] == "recentPaths":
                for recent_path in option_tag[0]:
                    path2timestamp[recent_path.attrib["value"]] = 0
            elif option_tag.attrib["name"] == "additionalInfo":
                add_info = option_tag[0]

        # for all additionalInfo entries, also add the real timestamp.
        if add_info is not None:
            for entry_tag in add_info:
                for option_tag in entry_tag[0][0]:
                    if (
                        option_tag.tag == "option"
                        and "name" in option_tag.attrib
                        and option_tag.attrib["name"] == "projectOpenTimestamp"
                    ):
                        path2timestamp[entry_tag.attrib["key"]] = int(
                            option_tag.attrib["value"]
                        )

        # return [(timestamp,path),...]
        return [
            (path2timestamp[path], path.replace("$USER_HOME$", HOME_DIR))
            for path in path2timestamp
        ]

    # finds the actual path to the relevant xml file of the most recent configuration directory
    def find_config_path(self, app_name: str):
        full_config_path = None

        xdg_dir = (
            GOOGLE_XDG_CONFIG_DIR
            if app_name == "AndroidStudio"
            else JETBRAINS_XDG_CONFIG_DIR
        )

        # newer versions (since 2020.1) put their configuration here
        if os.path.isdir(xdg_dir):
            # dirs contains possibly multiple directories for a program (eg. .GoLand2018.1 and .GoLand2017.3)
            dirs = [
                f
                for f in os.listdir(xdg_dir)
                if os.path.isdir(os.path.join(xdg_dir, f)) and f.startswith(app_name)
            ]
            # take the newest
            dirs.sort(reverse=True)
            if len(dirs) != 0:
                full_config_path = os.path.join(
                    xdg_dir, dirs[0], NEW_RELATIVE_CONFIG_PATH
                )

        # if no config was found in the newer path, repeat for the old ones
        if full_config_path is None or not os.path.exists(full_config_path):

            # dirs contains possibly multiple directories for a program (eg. .GoLand2018.1 and .GoLand2017.3)
            dirs = [
                f
                for f in os.listdir(HOME_DIR)
                if os.path.isdir(os.path.join(HOME_DIR, f))
                and f.startswith("." + app_name)
            ]
            # take the newest
            dirs.sort(reverse=True)
            if len(dirs) == 0:
                return None

            if app_name != "IntelliJIdea" and app_name != "AndroidStudio":
                full_config_path = os.path.join(
                    HOME_DIR, dirs[0], "config", OLD_RELATIVE_CONFIG_PATH
                )
            else:
                full_config_path = os.path.join(
                    HOME_DIR, dirs[0], "config", NEW_RELATIVE_CONFIG_PATH
                )

            if not os.path.exists(full_config_path):
                return None
        return full_config_path
