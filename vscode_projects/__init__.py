# -*- coding: utf-8 -*-
# Copyright (c) 2024 Sharsie

from albert import *
from dataclasses import dataclass
import os
import json
from pathlib import Path
import sqlite3
import threading
from urllib.parse import urlparse, unquote

md_iid = "3.0"
md_version = "1.11"
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
    isDirectory: bool
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
    # Location of the database with recent entries
    _stateDBPath = os.path.join(
        os.environ["HOME"],
        ".config/Code/User/globalStorage/state.vscdb"
    )

    # Location of the project manager configuration file
    _projectsPath = os.path.join(
        os.environ["HOME"],
        ".config/Code/User/globalStorage/alefragnani.project-manager/projects.json"
    )

    # Indicates whether results from the Recent list should be searched
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

    # Holds cached data from the configurations
    _configCache: dict[str, CachedConfig] = {}

    # Holds the last time the database was queried
    _dbLastQueryDBModTime: float = 0

    # Overrides the command to open projects
    _terminalCommand = ""

    # Setting indicating whether results from the Recent list should be searched
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

        if not os.path.exists(self._projectsPath):
            warning(
                "Project Manager search was enabled, but configuration file was not found")
            notif = Notification(
                title=self.name,
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

        if not os.path.exists(self._stateDBPath):
            warning("Could not find the state database")

        self._initConfiguration()

    def configWidget(self):
        return [
            {
                "type": "label",
                "text": """Recent files are sorted in order found in the state.
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
The way VSCode is opened can be overridden through terminal command.
This only works for projects, or recent directories, not workspaces or recent files.
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

        projectManagerEnabled = self.readConfig('projectManagerEnabled', bool)
        if projectManagerEnabled is None:
            # If not configured, check if the project manager configuration file exists and if so, enable PM search
            if os.path.exists(self._projectsPath):
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

        results: dict[str, SearchResult] = {}

        if query.string != "":
            matcher = Matcher(query.string)

            if self.recentEnabled:
                results = self._searchInRecentFiles(matcher, results)

            if self.projectManagerEnabled:
                results = self._searchInProjectManager(matcher, results)
        elif self.recentEnabled:
            results = self._searchInRecentFiles(Matcher(""), results)

        sortedItems = sorted(results.values(), key=lambda item: "%s_%s_%s" % (
            '{:03d}'.format(item.priority), '{:03d}'.format(item.sortIndex), item.project.name), reverse=False)

        items: list[StandardItem] = []
        for i in sortedItems:
            items.append(self._createItem(i.project))

        query.add(items)

    # Creates an item for the query based on the project and plugin settings
    def _createItem(self, project: Project) -> StandardItem:
        actions: list[Action] = []

        # Only add terminal command action if the project is a directory
        # Handling single files or workspaces would likely over-complicate the code and options
        if self.terminalCommand != "" and project.isDirectory:
            actions.append(
                Action(
                    id="open-terminal",
                    text=f"Run terminal command in project's workdir: {self.terminalCommand}",
                    callable=lambda: runTerminal(
                        f"cd {project.path} && {self.terminalCommand}")
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
            inputActionText=project.displayName,
            actions=actions,
        )

    def _searchInRecentFiles(self, matcher: Matcher, results: dict[str, SearchResult]) -> dict[str, SearchResult]:
        sortIndex = 1

        c = self._getDBConfig()
        for proj in c.projects:
            # Resolve symlinks to get unique results
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
        c = self._getProjectManagerConfig(self._projectsPath)
        for proj in c.projects:
            # Resolve symlinks to get unique results
            resolvedPath = str(Path(proj.path).resolve())

            if matcher.match(proj.name):
                results[resolvedPath] = self._getHigherPriorityResult(
                    SearchResult(
                        project=proj,
                        priority=self.priorityPMName,
                        sortIndex=0 if matcher.match(
                            proj.name).isExactMatch() else 1
                    ),
                    results.get(resolvedPath),
                )
                if self.priorityPMName < self.priorityPMPath and self.priorityPMName < self.priorityPMTag:
                    # PM name takes highest precedence, continue with next project
                    continue

            if matcher.match(proj.path) or matcher.match(resolvedPath):
                results[resolvedPath] = self._getHigherPriorityResult(
                    SearchResult(
                        project=proj,
                        priority=self.priorityPMPath,
                        sortIndex=1
                    ),
                    results.get(resolvedPath),
                )
                if self.priorityPMPath < self.priorityPMTag:
                    # PM path takes precedence over tags, continue with next project
                    continue

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
    # For nitpickers: higher priority = lower number
    def _getHigherPriorityResult(self, current: SearchResult, prev: SearchResult | None) -> SearchResult:
        if prev is None or current.priority < prev.priority or (current.priority == prev.priority and current.sortIndex < prev.sortIndex):
            return current

        return prev

    def _getDBConfig(self) -> CachedConfig:
        c: CachedConfig = self._configCache.get(
            self._stateDBPath, CachedConfig([], 0))

        # Do not proceed if the database does not exist
        # Storage location has been changing over time
        if not os.path.exists(self._stateDBPath):
            return c

        # Get the modification time of the database
        mTime = os.stat(self._stateDBPath).st_mtime

        # If the modification time is the same as the cached one, return the cached config
        if mTime == c.mTime:
            return c

        # While querying DB is in progress, return the cached config
        if self._dbLastQueryDBModTime == mTime:
            return c

        self._dbLastQueryDBModTime = mTime

        # Process the database and update cached config returning it
        def _process_storage():
            # Create a config with modification time of the database
            newConf = CachedConfig([], 0)
            newConf.mTime = mTime
            try:
                with sqlite3.connect(self._stateDBPath) as con:
                    # Load recent entries
                    for row in con.execute('SELECT * FROM "ItemTable" WHERE KEY = \'history.recentlyOpenedPathsList\''):
                        # Parse the recent entries into a json for further processing
                        data = json.loads(row[1])

                        for entry in data["entries"]:
                            isDirectory = False
                            isWorkspace = False

                            # Get the full path to the recent entry
                            if "folderUri" in entry:
                                isDirectory = True
                                parsed_uri = urlparse(
                                    entry["folderUri"]
                                )
                            elif "workspace" in entry:
                                isWorkspace = True
                                parsed_uri = urlparse(
                                    entry["workspace"]["configPath"]
                                )
                            elif "fileUri" in entry:
                                parsed_uri = urlparse(
                                    entry["fileUri"]
                                )
                            else:
                                continue

                            # Only support file URIs
                            if parsed_uri.scheme != "file":
                                continue

                            # Get the full path to the project
                            recentPath = Path(
                                unquote(parsed_uri.path)).as_posix()

                            # Make sure the path exists, so we skip removed directories
                            if not os.path.exists(recentPath):
                                continue

                            # Get the name of the project from the path
                            displayName = os.path.basename(recentPath)
                            if isWorkspace:
                                # Remove .code-workspace from the display name
                                if recentPath.endswith(".code-workspace"):
                                    displayName = displayName[:-15]
                                displayName += " (Workspace)"

                            # Add the project to the config
                            newConf.projects.append(Project(
                                displayName=displayName,
                                isDirectory=isDirectory,
                                name=displayName,
                                path=recentPath,
                                tags=[],
                            ))
            except Exception as e:
                warning(f"Failed to read the state database: {e}")

            # Update the cache only if this is the latest pass
            if self._dbLastQueryDBModTime == mTime:
                self._configCache[self._stateDBPath] = newConf

            return newConf

        # If the config was not loaded yet, block execution
        if c.mTime == 0:
            return _process_storage()

        # Process the database in a separate thread to update it in the background
        thread = threading.Thread(target=_process_storage)
        thread.start()

        # Return the cached config
        return c

    def _getProjectManagerConfig(self, path: str) -> CachedConfig:
        c = self._configCache.get(path, CachedConfig([], 0))

        # Do not proceed if the configuration file does not exist (e.g. PM was uninstalled while albert was running)
        if not os.path.exists(path):
            return c

        # Get the modification time of the configuration file
        mTime = os.stat(path).st_mtime

        # If the modification time is the same as the cached one, return the cached config
        if mTime == c.mTime:
            return c

        # Update the cached modification time
        c.mTime = mTime

        try:
            # Parse the configuration file
            with open(path) as configFile:
                configuredProjects = json.loads(configFile.read())

                for p in configuredProjects:
                    # Make sure we have necessary keys
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
                        isDirectory=True,
                        name=p["name"],
                        path=rootPath,
                        tags=[],
                    )

                    # Search against the query string
                    if "tags" in p:
                        for tag in p["tags"]:
                            project.tags.append(tag)

                    c.projects.append(project)

            # Update the cache
            self._configCache[path] = c
        except IOError:
            warning(f"Failed to read the PM configuration file: {path}")
        except (json.JSONDecodeError):
            warning(f"Failed to parse the PM configuration file: {path}")
        except Exception as e:
            warning(f"PM configuration file error: {e}")

        return c
