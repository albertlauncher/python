# -*- coding: utf-8 -*-
# Copyright (c) 2018-2023 Thomas Queste
# Copyright (c) 2023 Valentin Maerten

"""
This plugin allows you to quickly open projects of the Jetbrains IDEs

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
- WebStorm.

Note that for this plugin to find the IDEs, a commandline launcher in $PATH is required.
Open the IDE and click Tools -> Create Command-line Launcher to add one.

Disclaimer: This plugin has no affiliation with JetBrains s.r.o.. The icons are used under the terms specified here.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Union
from shutil import which
from sys import platform
from xml.etree import ElementTree
from albert import *

md_iid = '2.3'
md_version = "1.10"
md_name = "Jetbrains projects"
md_description = "Open your JetBrains projects"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/jetbrains_projects"
md_authors = ["@tomsquest", "@vmaerten", "@manuelschneid3r"]


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

    def __init__(self, name: str, icon: Path, config_dir_prefix: str, binaries: list[str]):
        self.name = name
        self.icon = icon
        self.config_dir_prefix = config_dir_prefix
        self.binary = self._find_binary(binaries)

    def _find_binary(self, binaries: list[str]) -> Union[str, None]:
        for binary in binaries:
            if which(binary):
                return binary
        return None

    def list_projects(self) -> list[Project]:
        config_dir = Path.home() / ".config"
        if platform == "darwin":
            config_dir = Path.home() / "Library" / "Application Support"

        dirs = list(config_dir.glob(f"{self.config_dir_prefix}*/"))
        if not dirs:
            return []
        latest = sorted(dirs)[-1]
        return self._parse_recent_projects(Path(latest) / "options" / "recentProjects.xml")

    def _parse_recent_projects(self, recent_projects_file: Path) -> list[Project]:
        try:
            root = ElementTree.parse(recent_projects_file).getroot()
            entries = root.findall(".//component[@name='RecentProjectsManager']//entry[@key]")

            projects = []
            for entry in entries:
                project_path = entry.attrib["key"].replace("$USER_HOME$", str(Path.home()))

                tag_opened = entry.find(".//option[@name='projectOpenTimestamp']")
                last_opened = tag_opened.attrib["value"] if tag_opened is not None and "value" in tag_opened.attrib else None

                if project_path and last_opened:
                    projects.append(
                        Project(name=Path(project_path).name, path=project_path, last_opened=int(last_opened))
                    )
            return projects
        except (ElementTree.ParseError, FileNotFoundError):
            return []


class Plugin(PluginInstance, TriggerQueryHandler):

    executables = []

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(
            self, self.id, self.name, self.description,
            defaultTrigger='jb '
        )

        plugin_dir = Path(__file__).parent
        editors = [
            Editor(
                name="Android Studio",
                icon=plugin_dir / "icons" / "androidstudio.svg",
                config_dir_prefix="Google/AndroidStudio",
                binaries=["studio", "androidstudio", "android-studio", "android-studio-canary", "jdk-android-studio",
                          "android-studio-system-jdk"]),
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
                binaries=["rider", "rider-eap"]),
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
        ]
        self.editors = [e for e in editors if e.binary is not None]

    def handleTriggerQuery(self, query: Query):
        editor_project_pairs = []
        for editor in self.editors:
            projects = editor.list_projects()
            projects = [p for p in projects if Path(p.path).exists()]
            projects = [p for p in projects if query.string.lower() in p.name.lower()]
            editor_project_pairs.extend([(editor, p) for p in projects])

        # sort by last opened
        editor_project_pairs.sort(key=lambda pair: pair[1].last_opened, reverse=True)

        query.add([self._make_item(editor, project, query) for editor, project in editor_project_pairs])

    def _make_item(self, editor: Editor, project: Project, query: Query) -> Item:
        return StandardItem(
            id="%s-%s-%s" % (editor.binary, project.path, project.last_opened),
            text=project.name,
            subtext=project.path,
            inputActionText=query.trigger + project.name,
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
