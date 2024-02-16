# -*- coding: utf-8 -*-
# Copyright (c) 2024 Sharsie

"""
Recent files are sorted in order found in the VSCode configuration.

Sort order with Project Manager can be adjusted, lower number = higher priority = displays first.

With all priorities equal, PM results will take precedence over recents.

PM extension: https://marketplace.visualstudio.com/items?itemName=alefragnani.project-manager

Terminal Command:

You can override how VSCode is opened.
Terminal will enter the working directory of the project upon selection and execute the desired command.

E.g. If you are using different environments based on the working dir, such as direnv, you can open
vscode by first executing direnv to load your environment by providing the following terminal command:

direnv exec . code .
"""

import os
import json
import unicodedata
from pathlib import Path
from dataclasses import dataclass
from albert import *

md_iid = "2.1"
md_version = "1.0"
md_name = "VSCode projects"
md_description = "Open VSCode projects"
md_url = "https://github.com/albertlauncher/python/tree/master/vscode_projects"
md_license = "MIT"
md_bin_dependencies = ["code"]
md_maintainers = "@Sharsie"

@dataclass
class Project:
    displayName: str
    name: str
    path: str
    tags: list[str]


@dataclass
class SearchResult:
    project: Project
    # priority is used to sort returned results
    priority: int
    # sortIndex is a decision maker when two search results have same priority
    sortIndex: int


@dataclass
class CachedConfig:
    projects: list[Project]
    mTime: float


class Plugin(PluginInstance, TriggerQueryHandler):
    # Possible locations for Code configuration
    _configStoragePaths = [
        os.path.join(os.environ["HOME"], ".config/Code/storage.json"),
        os.path.join(os.environ["HOME"],
                     ".config/Code/User/globalStorage/storage.json"),
    ]

    # Possible locations for Project Manager extension configuration
    _configProjectManagerPaths = [
        os.path.join(
            os.environ["HOME"], ".config/Code/User/globalStorage/alefragnani.project-manager/projects.json")
    ]

    # Indicates whether results from the Recent list in VSCode should be searched
    _recentEnabled = True

    # Indicates whether projects from Project Manager extension should be searched
    _projectManagerEnabled = False

    # Defines sorting priorities for results
    _sortPriority = {
        "PMName": 1,
        "PMPath": 5,
        "PMTag": 10,
        "Recent": 15
    }

    # Holds cached data from the json configurations
    _configCache: dict[str, CachedConfig] = {}

    # Overrides the command to open projects
    _terminalCommand = ""

    # Setting indicating whether results from the Recent list in VSCode should be searched
    @property
    def recentEnabled(self):
        return self._recentEnabled

    @recentEnabled.setter
    def recentEnabled(self, value):
        self._recentEnabled = value
        self.writeConfig("recentEnabled", value)

    # Setting indicating whether projects in Project Manager extension should be searched
    @property
    def projectManagerEnabled(self):
        return self._projectManagerEnabled

    @projectManagerEnabled.setter
    def projectManagerEnabled(self, value):
        self._projectManagerEnabled = value
        self.writeConfig("projectManagerEnabled", value)

        found = False
        for p in self._configProjectManagerPaths:
            if os.path.exists(p):
                found = True
                break

        if found == False:
            warning(
                "Project Manager search was enabled, but configuration file was not found")
            self.notification = Notification(
                title=f"{md_name}",
                body=f"Configuration file was not found for the Project Manager extension. Please make sure the extension is installed."
            )

    # Priority settings for project manager results using name search
    @property
    def priorityPMName(self):
        return self._sortPriority["PMName"]

    @priorityPMName.setter
    def priorityPMName(self, value):
        self._sortPriority["PMName"] = value
        self.writeConfig("priorityPMName", value)

    # Priority settings for project manager results using path search
    @property
    def priorityPMPath(self):
        return self._sortPriority["PMPath"]

    @priorityPMPath.setter
    def priorityPMPath(self, value):
        self._sortPriority["PMPath"] = value
        self.writeConfig("priorityPMPath", value)

    # Priority settings for project manager results using tag search
    @property
    def priorityPMTag(self):
        return self._sortPriority["PMTag"]

    @priorityPMTag.setter
    def priorityPMTag(self, value):
        self._sortPriority["PMTag"] = value
        self.writeConfig("priorityPMTag", value)

    # Priority settings for recently opened files
    @property
    def priorityRecent(self):
        return self._sortPriority["Recent"]

    @priorityRecent.setter
    def priorityRecent(self, value):
        self._sortPriority["Recent"] = value
        self.writeConfig("priorityRecent", value)

    # Setting for custom command when opening resulted items
    @property
    def terminalCommand(self):
        return self._terminalCommand

    @terminalCommand.setter
    def terminalCommand(self, value):
        self._terminalCommand = value
        self.writeConfig("terminalCommand", value)

    def __init__(self):
        TriggerQueryHandler.__init__(
            self,
            id=md_id,
            name=md_name,
            description=md_description,
            defaultTrigger="code ",
            synopsis="project name or path"
        )

        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/icon.svg"]
        self.notification = None

        configFound = False

        for p in self._configStoragePaths:
            if os.path.exists(p):
                configFound = True
                break

        if not configFound:
            warning("Could not find any VSCode configuration directory")

        self._initConfiguration()

    def configWidget(self):
        return [
            {
                "type": "checkbox",
                "property": "recentEnabled",
                "label": "Search in Recent files"
            },
            {
                "type": "checkbox",
                "property": "projectManagerEnabled",
                "label": "Search in Project Manager extension"
            },
            {
                "type": "spinbox",
                "property": "priorityPMName",
                "label": "Priority: Project Manager entries matched by name",
                "widget_properties": {
                    "minimum": 1,
                    "maximum": 99,
                },
            },
            {
                "type": "spinbox",
                "property": "priorityPMPath",
                "label": "Priority: Project Manager entries matched by path",
                "widget_properties": {
                    "minimum": 1,
                    "maximum": 99,
                },
            },
            {
                "type": "spinbox",
                "property": "priorityPMTag",
                "label": "Priority: Project Manager entries matched by tag",
                "widget_properties": {
                    "minimum": 1,
                    "maximum": 99,
                },
            },
            {
                "type": "spinbox",
                "property": "priorityRecent",
                "label": "Priority: Recent entries",
                "widget_properties": {
                    "minimum": 1,
                    "maximum": 99,
                },
            },
            {
                "type": "lineedit",
                "property": "terminalCommand",
                "label": "Run custom command in the workdir of selected item"
            },
        ]

    def _initConfiguration(self):
        # Recent search
        recentEnabled = self.readConfig('recentEnabled', bool)
        if recentEnabled is None:
            self._recentEnabled = True
            self.writeConfig("recentEnabled", True)
        else:
            self._recentEnabled = recentEnabled

        # Project Manager search
        foundPM = False
        for p in self._configProjectManagerPaths:
            if os.path.exists(p):
                foundPM = True
                break

        projectManagerEnabled = self.readConfig('projectManagerEnabled', bool)
        if projectManagerEnabled is None:
            # If not configured, check if the project manager configuration file exists and if so, enable PM search
            if foundPM:
                self._projectManagerEnabled = True
                self.writeConfig("projectManagerEnabled", True)
            else:
                self._projectManagerEnabled = False
        else:
            self._projectManagerEnabled = projectManagerEnabled

        # Priority settings
        for p in self._sortPriority:
            prio = self.readConfig(f"priority{p}", int)
            if prio is None:
                self.writeConfig(f"priority{p}", self._sortPriority[p])
            else:
                self._sortPriority[p] = prio

        # Terminal command setting
        terminalCommand = self.readConfig('terminalCommand', str)
        if terminalCommand is not None:
            self._terminalCommand = terminalCommand

    # Strings are normalized to match without accents and casing
    def _normalizeString(self, input: str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', input)
                       if unicodedata.category(c) != 'Mn').lower()

    def handleTriggerQuery(self, query):
        if not query.isValid:
            return

        # Normalize user query
        normalizedQuery = self._normalizeString(query.string.strip())

        if normalizedQuery == "":
            return

        results: dict[str, SearchResult] = {}

        if self.recentEnabled:
            results = self._searchInRecentFiles(normalizedQuery, results)

        if self.projectManagerEnabled:
            results = self._searchInProjectManager(normalizedQuery, results)

        sortedItems = sorted(results.values(), key=lambda item: "%s_%s_%s" % (
            '{:03d}'.format(item.priority), '{:03d}'.format(item.sortIndex), item.project.name), reverse=False)

        for i in sortedItems:
            query.add(self._createItem(i.project, query))

    # Creates an item for the query based on the project and plugin settings
    def _createItem(self, project: Project, query: TriggerQuery) -> StandardItem:
        actions: list[Action] = []

        if self.terminalCommand != "":
            actions.append(
                Action(
                    id="open-terminal",
                    text="Run a command through terminal in project's workdir",
                    callable=lambda: runTerminal(
                        close_on_exit=True,
                        script=self.terminalCommand,
                        workdir=project.path,
                    )
                )
            )
        else:
            actions.append(
                Action(
                    id="open-code",
                    text="Open VSCode",
                    callable=lambda: runDetachedProcess(
                        ["code", project.path]),
                )
            )

        return StandardItem(
            id=project.path,
            text=project.displayName,
            subtext=project.path,
            iconUrls=[f"file:{Path(__file__).parent}/icon.svg"],
            inputActionText=f"{query.trigger} {project.displayName}",
            actions=actions,
        )

    def _searchInRecentFiles(self, search: str, results: dict[str, SearchResult]) -> dict[str, SearchResult]:
        sortIndex = 1

        for path in self._configStoragePaths:
            c = self._getStorageConfig(path)
            for proj in c.projects:
                if proj.name.find(search) != -1 or proj.path.find(search) != -1:
                    results[proj.path] = self._getHigherPriorityResult(
                        SearchResult(
                            project=proj,
                            priority=self.priorityRecent,
                            sortIndex=sortIndex
                        ),
                        results.get(proj.path),
                    )

                if results.get(proj.path) is not None:
                    sortIndex += 1

        return results

    def _searchInProjectManager(self, search: str, results: dict[str, SearchResult]) -> dict[str, SearchResult]:
        for path in self._configProjectManagerPaths:
            c = self._getProjectManagerConfig(path)
            for proj in c.projects:
                if proj.name.find(search) != -1:
                    results[proj.path] = self._getHigherPriorityResult(
                        SearchResult(
                            project=proj,
                            priority=self.priorityPMName,
                            sortIndex=0 if proj.name == search else 1
                        ),
                        results.get(proj.path),
                    )

                if proj.path.find(search) != -1:
                    results[proj.path] = self._getHigherPriorityResult(
                        SearchResult(
                            project=proj,
                            priority=self.priorityPMPath,
                            sortIndex=1
                        ),
                        results.get(proj.path),
                    )

                for tag in proj.tags:
                    if tag.find(search) != -1:
                        results[proj.path] = self._getHigherPriorityResult(
                            SearchResult(
                                project=proj,
                                priority=self.priorityPMTag,
                                sortIndex=1
                            ),
                            results.get(proj.path),
                        )
                        break

        return results

    # Compares the search results to return the one with higher priority
    # For nitpickers: higher priorty = lower number
    def _getHigherPriorityResult(self, current: SearchResult, prev: SearchResult | None) -> SearchResult:
        if prev is None or current.priority < prev.priority or (current.priority == prev.priority and current.sortIndex < prev.sortIndex):
            return current

        return prev

    def _getStorageConfig(self, path: str) -> CachedConfig:
        c: CachedConfig = self._configCache.get(path, CachedConfig([], 0))

        if not os.path.exists(path):
            return c

        mTime = os.stat(path).st_mtime

        if mTime == c.mTime:
            return c

        c.mTime = mTime

        with open(path) as configFile:
            # Load the storage json
            storageConfig = json.loads(configFile.read())

            if (
                "lastKnownMenubarData" in storageConfig
                and "menus" in storageConfig["lastKnownMenubarData"]
                and "File" in storageConfig["lastKnownMenubarData"]["menus"]
                and "items" in storageConfig["lastKnownMenubarData"]["menus"]["File"]
            ):
                # These are all the menu items in File dropdown
                for menuItem in storageConfig["lastKnownMenubarData"]["menus"]["File"]["items"]:
                    # Cannot safely detect proper menu item, as menu item IDs change over time
                    # Instead we will search all submenus and check for IDs inside the submenu items
                    if (
                        not "id" in menuItem
                        or not "submenu" in menuItem
                        or not "items" in menuItem["submenu"]
                    ):
                        continue

                    for submenuItem in menuItem["submenu"]["items"]:
                        # Check of submenu item with id "openRecentFolder" and make sure it contains necessarry keys
                        if (
                            not "id" in submenuItem
                            or submenuItem['id'] != "openRecentFolder"
                            or not "enabled" in submenuItem
                            or submenuItem["enabled"] != True
                            or not "label" in submenuItem
                            or not "uri" in submenuItem
                            or not "path" in submenuItem["uri"]
                        ):
                            continue

                        # Get the full path to the project
                        recentPath = submenuItem["uri"]["path"]
                        if not os.path.exists(recentPath):
                            continue

                        displayName = recentPath.split("/")[-1]

                        # Inject the project
                        c.projects.append(Project(
                            displayName=displayName,
                            name=self._normalizeString(displayName),
                            path=recentPath,
                            tags=[],
                        ))

        return c

    def _getProjectManagerConfig(self, path: str) -> CachedConfig:
        c = self._configCache.get(path, CachedConfig([], 0))

        if not os.path.exists(path):
            return c

        mTime = os.stat(path).st_mtime

        if mTime == c.mTime:
            return c

        c.mTime = mTime

        with open(path) as configFile:
            configuredProjects = json.loads(configFile.read())

            for p in configuredProjects:
                # Make sure we have necessarry keys
                if (
                    not "rootPath" in p
                    or not "name" in p
                    or not "enabled" in p
                    or p["enabled"] != True
                ):
                    continue

                # Grab the path to the project
                rootPath = p["rootPath"]
                if os.path.exists(rootPath) == False:
                    continue

                project = Project(
                    displayName=p["name"],
                    name=self._normalizeString(p["name"]),
                    path=rootPath,
                    tags=[],
                )

                # Search against the query string
                if "tags" in p:
                    for tag in p["tags"]:
                        project.tags.append(self._normalizeString(tag))

                c.projects.append(project)

        return c
