"""
Supported IDEs:

Android Studio, CLion, DataGrip, DataSpell, GoLand, IntelliJ IDEA, PhpStorm, PyCharm, Rider, RubyMine, WebStorm.

Note: To open projects the command-line launcher is required. If your IDE has no \
command-line launcher in $PATH, use `Tools` > `Create Command-line Launcher`.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Union
from shutil import which
from sys import platform
from xml.etree import ElementTree
from albert import *

md_iid = '1.0'
md_version = "1.3"
md_name = "Jetbrains projects"
md_description = "Open your JetBrains projects"
md_license = "GPL-3"
md_url = "https://github.com/tomsquest/albert-jetbrains-projects-plugin"
md_maintainers = ["@mqus", "@tomsquest"]


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
        except ElementTree.ParseError:
            return []


class Plugin(TriggerQueryHandler):
    executables = []

    def id(self):
        return __name__

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "jb "

    def initialize(self):
        plugin_dir = Path(__file__).parent
        editors = [
            Editor(
                name="Android Studio",
                icon=plugin_dir / "androidstudio.svg",
                config_dir_prefix="Google/AndroidStudio",
                binaries=["studio", "androidstudio", "android-studio", "android-studio-canary", "jdk-android-studio",
                          "android-studio-system-jdk"]),
            Editor(
                name="CLion",
                icon=plugin_dir / "clion.svg",
                config_dir_prefix="JetBrains/CLion",
                binaries=["clion", "clion-eap"]),
            Editor(
                name="DataGrip",
                icon=plugin_dir / "datagrip.svg",
                config_dir_prefix="JetBrains/DataGrip",
                binaries=["datagrip", "datagrip-eap"]),
            Editor(
                name="DataSpell",
                icon=plugin_dir / "dataspell.svg",
                config_dir_prefix="JetBrains/DataSpell",
                binaries=["dataspell", "dataspell-eap"]),
            Editor(
                name="GoLand",
                icon=plugin_dir / "goland.svg",
                config_dir_prefix="JetBrains/GoLand",
                binaries=["goland", "goland-eap"]),
            Editor(
                name="IntelliJ IDEA",
                icon=plugin_dir / "idea.svg",
                config_dir_prefix="JetBrains/IntelliJIdea",
                binaries=["idea", "idea-ultimate", "idea-ce-eap", "idea-ue-eap", "intellij-idea-ce",
                          "intellij-idea-ce-eap", "intellij-idea-ue-bundled-jre", "intellij-idea-ultimate-edition",
                          "intellij-idea-community-edition-jre", "intellij-idea-community-edition-no-jre"]),
            Editor(
                name="PhpStorm",
                icon=plugin_dir / "phpstorm.svg",
                config_dir_prefix="JetBrains/PhpStorm",
                binaries=["phpstorm", "phpstorm-eap"]),
            Editor(
                name="PyCharm",
                icon=plugin_dir / "pycharm.svg",
                config_dir_prefix="JetBrains/PyCharm",
                binaries=["charm", "pycharm", "pycharm-eap"]),
            Editor(
                name="Rider",
                icon=plugin_dir / "rider.svg",
                config_dir_prefix="JetBrains/Rider",
                binaries=["rider", "rider-eap"]),
            Editor(
                name="RubyMine",
                icon=plugin_dir / "rubymine.svg",
                config_dir_prefix="JetBrains/RubyMine",
                binaries=["rubymine", "rubymine-eap", "jetbrains-rubymine", "jetbrains-rubymine-eap"]),
            Editor(
                name="WebStorm",
                icon=plugin_dir / "webstorm.svg",
                config_dir_prefix="JetBrains/WebStorm",
                binaries=["webstorm", "webstorm-eap"]),
        ]
        self.editors = [e for e in editors if e.binary is not None]

    def handleTriggerQuery(self, query: TriggerQuery):
        editor_project_pairs = []
        for editor in self.editors:
            projects = editor.list_projects()
            projects = [p for p in projects if Path(p.path).exists()]
            projects = [p for p in projects if query.string.lower() in p.name.lower()]
            editor_project_pairs.extend([(editor, p) for p in projects])

        # sort by last opened
        editor_project_pairs.sort(key=lambda pair: pair[1].last_opened, reverse=True)

        query.add([self._make_item(editor, project, query) for editor, project in editor_project_pairs])

    def _make_item(self, editor: Editor, project: Project, query: TriggerQuery) -> Item:
        return Item(
            id="%s-%s-%s" % (editor.binary, project.path, project.last_opened),
            text=project.name,
            subtext=project.path,
            completion=query.trigger + project.name,
            icon=[str(editor.icon)],
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
