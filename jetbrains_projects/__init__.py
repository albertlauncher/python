# -*- coding: utf-8 -*-
# Copyright (c) 2018-2023 Thomas Queste
# Copyright (c) 2023 Valentin Maerten

"""
This plugin allows you to quickly open projects of the Jetbrains IDEs

- Aqua
- Android Studio
- CLion
- DataGrip
- DataSpell
- GoLand
- IntelliJ IDEA
- PhpStorm
- PyCharm
- Rider
- RubyMine
- WebStorm
- Writerside.

Note that for this plugin to find the IDEs, a commandline launcher in $PATH is required.
Open the IDE and click Tools -> Create Command-line Launcher to add one.

Disclaimer: This plugin has no affiliation with JetBrains s.r.o.. The icons are used under the terms specified here.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Union, List
from shutil import which
from sys import platform
from xml.etree import ElementTree
from albert import *

md_iid = "3.0"
md_version = "3.0"
md_name = "Jetbrains projects"
md_description = "Open your JetBrains projects"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/jetbrains_projects"
md_authors = ["@tomsquest", "@vmaerten", "@manuelschneid3r", "@d3v2a"]


@dataclass
class Project:
    name: str
    path: str
    last_opened: int


@dataclass
class Editor:
    name: str
    icon: Path
    config_dir_prefix: str
    binary: str

    # Rider calls recentProjects.xml -> recentSolutions.xml and in it RecentProjectsManager -> RiderRecentProjectsManager
    is_rider: bool

    def __init__(
            self,
            name: str,
            icon: Path,
            config_dir_prefix: str,
            binaries: list[str],
            is_rider = False):
        self.name = name
        self.icon = icon
        self.config_dir_prefix = config_dir_prefix
        self.binary = self._find_binary(binaries)
        self.is_rider = is_rider

    @staticmethod
    def _find_binary(binaries: list[str]) -> Union[str, None]:
        for binary in binaries:
            if which(binary):
                return binary
        return None

    def list_projects(self) -> List[Project]:
        config_dir = Path.home() / ".config"
        if platform == "darwin":
            config_dir = Path.home() / "Library" / "Application Support"

        dirs = list(config_dir.glob(f"{self.config_dir_prefix}*/"))
        if not dirs:
            return []
        latest = sorted(dirs)[-1]
        if not self.is_rider:
            recent_projects_xml = "recentProjects.xml"
        else:
            recent_projects_xml = "recentSolutions.xml"
        return self._parse_recent_projects(Path(latest) / "options" / recent_projects_xml)

    def _parse_recent_projects(self, recent_projects_file: Path) -> list[Project]:
        try:
            root = ElementTree.parse(recent_projects_file).getroot()
            if not self.is_rider:
                entries = root.findall(".//component[@name='RecentProjectsManager']//entry[@key]")
            else:
                entries = root.findall(".//component[@name='RiderRecentProjectsManager']//entry[@key]")

            projects = []
            for entry in entries:
                project_path = entry.attrib["key"]
                project_path = project_path.replace("$USER_HOME$", str(Path.home()))
                project_name = Path(project_path).name
                files = Path(project_path + "/.idea").glob("*.iml")
                tag_opened = entry.find(".//option[@name='projectOpenTimestamp']")
                last_opened = tag_opened.attrib["value"] if tag_opened is not None and "value" in tag_opened.attrib else None

                if project_path and last_opened:
                    projects.append(
                        Project(name=project_name, path=project_path, last_opened=int(last_opened))
                    )
                for file in files:
                    name = file.name.replace(".iml", "")
                    if name != project_name:
                        projects.append(Project(name=name, path=project_path, last_opened=int(last_opened)))

            return projects
        except (ElementTree.ParseError, FileNotFoundError):
            return []


class Plugin(PluginInstance, TriggerQueryHandler):

    executables = []

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

        self.fuzzy = False

        plugin_dir = Path(__file__).parent
        editors = [
            Editor(
                name="Android Studio",
                icon=plugin_dir / "icons" / "androidstudio.svg",
                config_dir_prefix="Google/AndroidStudio",
                binaries=["studio", "androidstudio", "android-studio", "android-studio-canary", "jdk-android-studio",
                          "android-studio-system-jdk"]),
            Editor(
                name="Aqua",
                icon=plugin_dir / "icons" / "aqua.svg",
                config_dir_prefix="JetBrains/Aqua",
                binaries=["aqua", "aqua-eap"]),
            Editor(
                name="CLion",
                icon=plugin_dir / "icons" / "clion.svg",
                config_dir_prefix="JetBrains/CLion",
                binaries=["clion", "clion-eap"]),
            Editor(
                name="DataGrip",
                icon=plugin_dir / "icons" / "datagrip.svg",
                config_dir_prefix="JetBrains/DataGrip",
                binaries=["datagrip", "datagrip-eap"]),
            Editor(
                name="DataSpell",
                icon=plugin_dir / "icons" / "dataspell.svg",
                config_dir_prefix="JetBrains/DataSpell",
                binaries=["dataspell", "dataspell-eap"]),
            Editor(
                name="GoLand",
                icon=plugin_dir / "icons" / "goland.svg",
                config_dir_prefix="JetBrains/GoLand",
                binaries=["goland", "goland-eap"]),
            Editor(
                name="IntelliJ IDEA",
                icon=plugin_dir / "icons" / "idea.svg",
                config_dir_prefix="JetBrains/IntelliJIdea",
                binaries=["idea", "idea.sh", "idea-ultimate", "idea-ce-eap", "idea-ue-eap", "intellij-idea-ce",
                          "intellij-idea-ce-eap", "intellij-idea-ue-bundled-jre", "intellij-idea-ultimate-edition",
                          "intellij-idea-community-edition-jre", "intellij-idea-community-edition-no-jre"]),
            Editor(
                name="PhpStorm",
                icon=plugin_dir / "icons" / "phpstorm.svg",
                config_dir_prefix="JetBrains/PhpStorm",
                binaries=["phpstorm", "phpstorm-eap"]),
            Editor(
                name="PyCharm",
                icon=plugin_dir / "icons" / "pycharm.svg",
                config_dir_prefix="JetBrains/PyCharm",
                binaries=["charm", "pycharm", "pycharm-eap"]),
            Editor(
                name="Rider",
                icon=plugin_dir / "icons" / "rider.svg",
                config_dir_prefix="JetBrains/Rider",
                binaries=["rider", "rider-eap"],
                is_rider=True),
            Editor(
                name="RubyMine",
                icon=plugin_dir / "icons" / "rubymine.svg",
                config_dir_prefix="JetBrains/RubyMine",
                binaries=["rubymine", "rubymine-eap", "jetbrains-rubymine", "jetbrains-rubymine-eap"]),
            Editor(
                name="WebStorm",
                icon=plugin_dir / "icons" / "webstorm.svg",
                config_dir_prefix="JetBrains/WebStorm",
                binaries=["webstorm", "webstorm-eap"]),
            Editor(
                name="RustRover",
                icon=plugin_dir / "icons" / "rustrover.svg",
                config_dir_prefix="JetBrains/RustRover",
                binaries=["rustrover", "rustrover-eap"]),
            Editor(
                name="Writerside",
                icon=plugin_dir / "icons" / "writerside.svg",
                config_dir_prefix="JetBrains/Writerside",
                binaries=["writerside", "writerside-eap"]),
        ]
        self.editors = [e for e in editors if e.binary is not None]

    def supportsFuzzyMatching(self):
        return True

    def setFuzzyMatching(self, enabled):
        self.fuzzy = enabled

    def defaultTrigger(self):
        return "jb "

    def handleTriggerQuery(self, query: Query):
        editor_project_pairs = []

        m = Matcher(query.string, MatchConfig(fuzzy=self.fuzzy))

        for editor in self.editors:
            for project in editor.list_projects():
                if Path(project.path).exists() and m.match(project.name, project.path):
                    editor_project_pairs.append((editor, project))

        # sort by last opened
        editor_project_pairs.sort(key=lambda pair: pair[1].last_opened, reverse=True)

        query.add([self._make_item(editor, project) for editor, project in editor_project_pairs])

    @staticmethod
    def _make_item(editor: Editor, project: Project) -> Item:
        return StandardItem(
            id="%s-%s-%s" % (editor.binary, project.path, project.last_opened),
            text=project.name,
            subtext=project.path,
            inputActionText=project.name,
            iconUrls=["file:" + str(editor.icon)],
            actions=[
                Action(
                    "Open",
                    "Open in %s" % editor.name,
                    lambda selected_project=project.path: runDetachedProcess(
                        [editor.binary, selected_project]
                    ),
                )
            ],
        )

    def configWidget(self):
        return [
            {
                'type': 'label',
                'text': __doc__.strip(),
                'widget_properties': {
                    'textFormat': 'Qt::MarkdownText'
                }
            }
        ]
