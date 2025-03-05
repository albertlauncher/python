# -*- coding: utf-8 -*-

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
from rapidfuzz import fuzz

md_iid = '2.5'
md_version = "1.3"
md_name = "GitHub repositories"
md_description = "Open GitHub user repositories in the browser"
md_license = "GPL-3.0"
md_url = 'https://github.com/albertlauncher/python/tree/main/github'
md_authors = "@aironskin"
md_lib_dependencies = ["github3.py", "rapidfuzz", "keyring"]

plugin_dir = os.path.dirname(__file__)
CACHE_FILE = os.path.join(plugin_dir, "repository_cache.json")


class Plugin(PluginInstance, TriggerQueryHandler):

    # initialize the plugin
    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(
            self,
            id=self.id,
            name=self.name,
            description=self.description,
            defaultTrigger='gh '
        )
        self.iconUrls = [f"file:{Path(__file__).parent}/plugin.svg"]

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

    # perform fuzzy search on the repositories
    def fuzzy_search_repositories(self, repositories, search_string):
        matching_repos = []
        for repo in repositories:
            repo_name = repo["name"]
            ratio = fuzz.token_set_ratio(
                repo_name.lower(), search_string.lower())
            if ratio >= 75:
                matching_repos.append(repo)
        return matching_repos

    def handleTriggerQuery(self, query):
        # load github user token
        token = self.load_token()
        if not token:
            query.add(StandardItem(
                id=self.id,
                text=self.name,
                iconUrls=self.iconUrls,
                subtext="Paste your GitHub token and press [enter] to save it",
                actions=[
                    Action("save", "Save token", lambda t=query.string.strip(): self.save_token(t))]
            ))

        # load the repositories from cache or fetch them from github
        repositories = self.load_cached_repositories()
        if not repositories:
            query.add(StandardItem(
                id=self.id,
                text=self.name,
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
                    id=self.id,
                    text=self.name,
                    iconUrls=self.iconUrls,
                    subtext="Press [enter] to rebuild the local repository cache (may take a few seconds)",
                    actions=[Action("rebuild", "Rebuild repository cache", lambda: self.cache_repositories(
                        self.get_user_repositories(token)))]
                ))

            if not repositories:
                return []

            # fuzzy search the query in repository names
            search_term = query.string.strip().lower()
            exact_matches = []
            fuzzy_matches = []

            for repo in repositories:
                repo_name = repo["name"]
                if repo_name.lower().startswith(search_term):
                    exact_matches.append(repo)
                else:
                    similarity_ratio = fuzz.token_set_ratio(
                        repo_name.lower(), search_term)
                    if similarity_ratio > 25:
                        fuzzy_matches.append((repo, similarity_ratio))

            # sort the fuzzy matches based on similarity ratio
            fuzzy_matches.sort(key=lambda x: x[1], reverse=True)

            # return the results
            results = []
            for repo in exact_matches:
                results.append(StandardItem(
                    id=self.id,
                    text=repo["name"],
                    iconUrls=self.iconUrls,
                    subtext=repo["full_name"],
                    actions=[Action("eopen", "Open exact match",
                                    lambda u=repo["html_url"]: openUrl(u))]
                ))

            for repo, similarity_ratio in fuzzy_matches:
                results.append(StandardItem(
                    id=self.id,
                    text=repo["name"],
                    iconUrls=self.iconUrls,
                    subtext=repo["full_name"],
                    actions=[Action("fopen", "Open fuzzy match",
                                    lambda u=repo["html_url"]: openUrl(u))]
                ))

            if results:
                query.add(results)
            else:
                query.add(StandardItem(
                    id=self.id,
                    text="No repositories matching search string",
                    iconUrls=self.iconUrls
                ))

        else:
            query.add(StandardItem(
                id=self.id,
                iconUrls=self.iconUrls,
                text="...",
                subtext="Search for a GitHub user repository name"
            ))
