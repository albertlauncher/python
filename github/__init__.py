# -*- coding: utf-8 -*-
# Copyright (c) 2024 Stefan Schnyder

"""
Searches GitHub user repositories and opens the selected match in the browser
Trigger with 'gh '
Rebuild cache with 'gh rebuild cache'
"""

import os
import json
import keyring
from albert import *
from pathlib import Path
import github3

md_iid = '3.0'
md_version = "1.5"
md_name = "GitHub repositories"
md_description = "Open GitHub user repositories in the browser"
md_license = "MIT"
md_url = 'https://github.com/albertlauncher/python/tree/main/github'
md_authors = "@aironskin"
md_lib_dependencies = ["github3.py", "keyring"]

plugin_dir = os.path.dirname(__file__)
CACHE_FILE = os.path.join(plugin_dir, "repository_cache.json")


class Plugin(PluginInstance, TriggerQueryHandler):

    # set the icon
    iconUrls = [f"file:{Path(__file__).parent}/plugin.svg"]

    # initialize the plugin
    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

        self._fuzzy = self.readConfig("fuzzy", bool)
        if self._fuzzy is None:
            self._fuzzy = False

    @property
    def fuzzy(self):
        return self._fuzzy

    @fuzzy.setter
    def fuzzy(self, value):
        self._fuzzy = value
        self.writeConfig("fuzzy", value)

    def configWidget(self):
        return [
            {
                "type": "checkbox",
                "label": "Enable fuzzy matching for repository names",
                "property": "fuzzy",
            }
        ]

    def defaultTrigger(self):
        return 'gh '

    # persist the github token in the keyring
    def save_token(self, token):
        keyring.set_password("albert-github", "github_token", token)

    # load the token from the keyring
    def load_token(self):
        return keyring.get_password("albert-github", "github_token")

    # fetch user repositories from github
    def get_user_repositories(self, token):
        g = github3.login(token=token)
        user = g.me()
        repositories = []

        for repo in g.repositories():
            repositories.append(
                {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "html_url": repo.html_url,
                }
            )

        repositories.sort(key=lambda repo: repo["name"].lower())

        return repositories

    # cache the repositories on the file system
    def cache_repositories(self, repositories):
        with open(CACHE_FILE, "w") as file:
            json.dump(repositories, file)

    # load the cached repositories from the file if it exists
    def load_cached_repositories(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as file:
                return json.load(file)
        return None

    def handleTriggerQuery(self, query):
        # load github user token
        token = self.load_token()
        if not token:
            query.add(StandardItem(
                id=self.id(),
                text=self.name(),
                iconUrls=self.iconUrls,
                subtext="Paste your GitHub token and press [enter] to save it",
                actions=[
                    Action("save", "Save token", lambda t=query.string.strip(): self.save_token(t))]
            ))

        # load the repositories from cache or fetch them from github
        repositories = self.load_cached_repositories()
        if not repositories:
            query.add(StandardItem(
                id=self.id(),
                text=self.name(),
                iconUrls=self.iconUrls,
                subtext="Press [enter] to initialize the repository cache (may take a few seconds)",
                actions=[Action("cache", "Create repository cache", lambda: self.cache_repositories(
                    self.get_user_repositories(token)))]
            ))

        query_stripped = query.string.strip()

        if query_stripped:

            # refresh local repositories cache
            if query_stripped.lower() == "rebuild cache":
                query.add(StandardItem(
                    id=self.id(),
                    text=self.name(),
                    iconUrls=self.iconUrls,
                    subtext="Press [enter] to rebuild the local repository cache (may take a few seconds)",
                    actions=[Action("rebuild", "Rebuild repository cache", lambda: self.cache_repositories(
                        self.get_user_repositories(token)))]
                ))

            if not repositories:
                return []

            # match the query with the cached repositories
            m = Matcher(query.string, MatchConfig(fuzzy=self.fuzzy))
            matching_repos = [
                repo for repo in repositories if m.match(repo["name"])
            ]

            # return the results
            results = []
            for repo in matching_repos:
                results.append(StandardItem(
                    id=self.id(),
                    text=repo["name"],
                    iconUrls=self.iconUrls,
                    subtext=repo["full_name"],
                    actions=[Action("open", "Open repository",
                                    lambda u=repo["html_url"]: openUrl(u))]
                ))

            if results:
                query.add(results)
            else:
                query.add(StandardItem(
                    id=self.id(),
                    text="No repositories matching search string",
                    iconUrls=self.iconUrls
                ))

        else:
            query.add(StandardItem(
                id=self.id(),
                iconUrls=self.iconUrls,
                text="...",
                subtext="Search for a GitHub user repository name"
            ))
