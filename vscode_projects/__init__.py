# -*- coding: utf-8 -*-
# Copyright (c) 2024 Sharsie

import os
import json
from pathlib import Path
from dataclasses import dataclass
from albert import *

md_iid = "3.0"
md_version = "1.9"
md_name = "VSCode projects"
md_description = "Open VSCode projects"
md_url = "https://github.com/albertlauncher/python/tree/master/vscode_projects"
md_license = "MIT"
md_bin_dependencies = ["code"]
md_authors = ["@Sharsie"]

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
            notif = Notification(
                title=f"{self.name}",
                text=f"Configuration file was not found for the Project Manager extension. Please make sure the extension is installed."
            )
            notif.send()

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

    def defaultTrigger(self):
        return "code "

    def synopsis(self, query):
        return "project name or path"

    def __init__(self):
        self.iconUrls = [f"file:{Path(__file__).parent}/icon.svg"]

        PluginInstance.__init__(self)

        TriggerQueryHandler.__init__(self)

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
                "type": "label",
                "text": """Recent files are sorted in order found in the VSCode configuration.
Sort order with Project Manager can be adjusted, lower number = higher priority = displays first.
With all priorities equal, PM results will take precedence over recents."""
            },
            {
                "type": "label",
                "text": """
PM extension: https://marketplace.visualstudio.com/items?itemName=alefragnani.project-manager
"""
            },

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
                "type": "label",
                "text": """
The way VSCode is opened can be overriden through terminal command.
Terminal will enter the working directory of the project upon selection, execute the command and then close itself.

Usecase with direnv - To load direnv environment before opening VSCode, enter the following custom command: direnv exec . code .

Usecase with single VSCode instance - To reuse the VSCode window instead of opening a new one, enter the following custom command: code -r ."""
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

    def handleTriggerQuery(self, query):
        if not query.isValid:
            return

        if query.string == "":
            return

        matcher = Matcher(query.string)

        results: dict[str, SearchResult] = {}

        if self.recentEnabled:
            results = self._searchInRecentFiles(matcher, results)

        if self.projectManagerEnabled:
            results = self._searchInProjectManager(matcher, results)

        sortedItems = sorted(results.values(), key=lambda item: "%s_%s_%s" % (
            '{:03d}'.format(item.priority), '{:03d}'.format(item.sortIndex), item.project.name), reverse=False)

        items: list[StandardItem] = []
        for i in sortedItems:
            items.append(self._createItem(i.project, query))

        query.add(items)

    # Creates an item for the query based on the project and plugin settings
    def _createItem(self, project: Project, query: Query) -> StandardItem:
        actions: list[Action] = []

        if self.terminalCommand != "":
            actions.append(
                Action(
                    id="open-terminal",
                    text=f"Run terminal command in project's workdir: {self.terminalCommand}",
                    callable=lambda: runTerminal(f"cd {project.path} && {self.terminalCommand}")
                )
            )

        actions.append(
            Action(
                id="open-code",
                text="Open with VSCode",
                callable=lambda: runDetachedProcess(
                    ["code", project.path]),
            )
        )

        subtext = ""

        if len(project.tags) > 0:
            subtext = "<" + ",".join(project.tags) + "> "

        return StandardItem(
            id=project.path,
            text=project.displayName,
            subtext=f"{subtext}{project.path}",
            iconUrls=self.iconUrls,
            inputActionText=f"{query.trigger}{project.displayName}",
            actions=actions,
        )

    def _searchInRecentFiles(self, matcher: Matcher, results: dict[str, SearchResult]) -> dict[str, SearchResult]:
        sortIndex = 1

        for path in self._configStoragePaths:
            c = self._getStorageConfig(path)
            for proj in c.projects:
                # Resolve sym links to get unique results
                resolvedPath = str(Path(proj.path).resolve())
                if matcher.match(proj.name) or matcher.match(proj.path) or matcher.match(resolvedPath):
                    results[resolvedPath] = self._getHigherPriorityResult(
                        SearchResult(
                            project=proj,
                            priority=self.priorityRecent,
                            sortIndex=sortIndex
                        ),
                        results.get(resolvedPath),
                    )

                if results.get(resolvedPath) is not None:
                    sortIndex += 1

        return results

    def _searchInProjectManager(self, matcher: Matcher, results: dict[str, SearchResult]) -> dict[str, SearchResult]:
        for path in self._configProjectManagerPaths:
            c = self._getProjectManagerConfig(path)
            for proj in c.projects:
                # Resolve sym links to get unique results
                resolvedPath = str(Path(proj.path).resolve())
                if matcher.match(proj.name):
                    results[resolvedPath] = self._getHigherPriorityResult(
                        SearchResult(
                            project=proj,
                            priority=self.priorityPMName,
                            sortIndex=0 if matcher.match(proj.name).isExactMatch() else 1
                        ),
                        results.get(resolvedPath),
                    )

                if matcher.match(proj.path) or matcher.match(resolvedPath):
                    results[resolvedPath] = self._getHigherPriorityResult(
                        SearchResult(
                            project=proj,
                            priority=self.priorityPMPath,
                            sortIndex=1
                        ),
                        results.get(resolvedPath),
                    )

                for tag in proj.tags:
                    if matcher.match(tag):
                        results[resolvedPath] = self._getHigherPriorityResult(
                            SearchResult(
                                project=proj,
                                priority=self.priorityPMTag,
                                sortIndex=1
                            ),
                            results.get(resolvedPath),
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
                            name=displayName,
                            path=recentPath,
                            tags=[],
                        ))

        self._configCache[path] = c

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
                    name=p["name"],
                    path=rootPath,
                    tags=[],
                )

                # Search against the query string
                if "tags" in p:
                    for tag in p["tags"]:
                        project.tags.append(tag)

                c.projects.append(project)

        self._configCache[path] = c

        return c
