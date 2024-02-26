# -*- coding: utf-8 -*-
# Copyright (c) 2024 Chi-Sheng Liu

"""
Open the URLs defined in the local plain text file.

See https://github.com/albertlauncher/python/local_bookmark for details
"""

from albert import *
from pathlib import Path
import webbrowser

md_iid = '2.0'
md_version = '1.0'
md_name = 'Local Bookmark'
md_description = 'Open locally defined URLs  in browser'
md_license = "MIT"
md_url = 'https://github.com/albertlauncher/python/local_bookmark'
md_authors = "@MortalHappiness"


class LocalBookmarkPluginError(Exception):
    pass


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     defaultTrigger='lb ')
        PluginInstance.__init__(self, extensions=[self])

        self._file_path = self.readConfig('file_path', str)
        if self._file_path is None:
            self._file_path = ""

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value
        self.writeConfig('file_path', value)

    def configWidget(self):
        return [
            {
                "type": "lineedit",
                "label": "Bookmark file path",
                "property": "file_path",
            },
        ]

    def handleTriggerQuery(self, query):
        # file_path = "/home/mortalhappiness/pCloudDrive/BACKUP/Settings/albert/local_bookmark.txt"
        file_path = self.file_path

        try:
            if not file_path:
                raise LocalBookmarkPluginError("Please set the bookmark file path in the configuration.")
            if not Path(file_path).is_file():
                raise LocalBookmarkPluginError("The file does not exist. Please create one.")
        except LocalBookmarkPluginError as e:
            query.add(
                StandardItem(
                    id=md_name,
                    text="Error",
                    subtext=str(e),
                    iconUrls=["xdg:error"],
                )
            )
            return

        # Parse the file
        keyword_to_urls = {}
        current_keywords = ()
        for line in Path(file_path).read_text().split("\n"):
            if not line:
                continue
            if line.startswith("#"):
                current_keywords = tuple(keyword.strip().lower() for keyword in line[1:].split(","))
                continue
            for keyword in current_keywords:
                keyword_to_urls.setdefault(keyword, []).append(line)

        search = query.string.strip().lower()
        if not search:
            query.add(
                StandardItem(
                    id=md_name,
                    text="Open the local bookmark file in editor",
                    iconUrls=["xdg:text"],
                    actions=[Action("config", "Open the local bookmark file in editor",
                                    lambda: runDetachedProcess(["xdg-open", file_path]))]
                )
            )
            return

        for keyword, urls in sorted(keyword_to_urls.items()):
            if search in keyword:
                for url in urls:
                    query.add(
                        StandardItem(
                            id=md_name,
                            text=keyword,
                            subtext=url,
                            iconUrls=["xdg:browser"],
                            actions=[Action("open", "Open in browser", lambda u=url: webbrowser.open(u))]
                        )
                    )
