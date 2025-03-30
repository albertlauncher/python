# -*- coding: utf-8 -*-
# Copyright (c) 2024 Ludovic Dehon

"""
Search Github repositories, issues or pull request
"""
import datetime
from pathlib import Path
from time import sleep

from albert import *

from github import Github
from github import Auth
import timeago

md_iid = "3.0"
md_version = "2.0"
md_name = "Github"
md_description = "Search Github repositories, issues or pull request"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/github"
md_authors = "@tchiotludo"
md_lib_dependencies = ["PyGithub", "timeago"]


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

        self.iconUrls = [f"file:{Path(__file__).parent}/github.svg"]

        self._token = self.readConfig("token", str)
        if self._token is None:
            self._token = ""

        self._filters = self.readConfig("filters", str)
        if self._filters is None:
            self._filters = "is:open"

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        self.writeConfig("token", value)

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, value):
        self._filters = value
        self.writeConfig("filters", value)

    def defaultTrigger(self):
        return "gh "

    def configWidget(self):
        return [
            {
                "type": "lineedit",
                "property": "token",
                "label": "Personal access token",
            },
            {
                "type": "lineedit",
                "property": "filters",
                "label": "Default issues or pull request filters",
            }
        ]

    def synopsis(self, s):
        return "[r] [i] [p] [*] search"

    def _repository(self, repository_url):
        return "/".join(repository_url.split("/")[-2:])

    def handleTriggerQuery(self, query):
        if self.token != "":
            auth = Auth.Token(self.token)
            g = Github(auth=auth)
        else:
            g = Github()

        stripped = query.string.strip()
        now = datetime.datetime.now(datetime.UTC)

        if stripped:
            # dont flood
            for _ in range(25):
                sleep(0.01)
                if not query.isValid:
                    return

            splits = stripped.split()
            try:
                if splits[0] == "r":
                    result = g.get_user().get_repos(sort="updated")
                    text = " ".join(splits[1:])

                    info(f"Starting get_user get_repos filter by {text}")

                    count = 0
                    for repo in result:
                        if text != "" and repo.full_name.find(text) == -1:
                            continue

                        count = count + 1
                        query.add(StandardItem(
                            id=self.id(),
                            text=repo.full_name,
                            iconUrls=self.iconUrls,
                            actions=[Action("open", "Open link", lambda u=repo.html_url: openUrl(u))]
                        ))

                    if count == 0:
                        query.add(StandardItem(
                            id=self.id(),
                            text="No repository found",
                            subtext=f"for query: {text}",
                            iconUrls=self.iconUrls,
                        ))

                else:
                    search_query = self._filters
                    text = stripped

                    if splits[0] == "p":
                        search_query = f"{search_query} is:pr "
                        text = " ".join(splits[1:])
                    if splits[0] == "i":
                        search_query = f"{search_query} is:issue "
                        text = " ".join(splits[1:])
                    if splits[0] == "*":
                        search_query = ""
                        text = " ".join(splits[1:])

                    search_query = f"{search_query} {text}"

                    info(f"Starting query {search_query}")

                    result = g.search_issues(search_query).get_page(0)

                    if len(result) == 0:
                        query.add(StandardItem(
                            id=self.id(),
                            text="No issues found",
                            subtext=f"for query: {search_query}",
                            iconUrls=self.iconUrls,
                        ))

                    for issue in result:
                        query.add(StandardItem(
                            id=self.id(),
                            text=issue.title,
                            subtext=f"[#{issue.number}] "
                                    f"[{issue.state}] "
                                    f"[{self._repository(issue.repository_url)}] "
                                    f"created by {issue.user.login}, "
                                    f"updated {timeago.format(issue.updated_at, now)}",
                            iconUrls=self.iconUrls,
                            actions=[Action("open", "Open link", lambda u=issue.html_url: openUrl(u))]
                        ))

            except Exception as e:
                query.add(StandardItem(
                    id=self.id(),
                    text="Error",
                    subtext=str(e),
                    iconUrls=self.iconUrls
                ))

                warning(str(e))
