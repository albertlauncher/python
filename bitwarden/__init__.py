# -*- coding: utf-8 -*-

import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from subprocess import CalledProcessError, run

from albert import *

md_iid = "3.0"
md_version = "3.1"
md_name = "Bitwarden"
md_description = "'rbw' wrapper extension"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/bitwarden"
md_authors = ["@ovitor", "@daviddeadly", "@manuelschneid3r"]
md_bin_dependencies = ["rbw"]

MAX_MINUTES_CACHE_TIMEOUT = 60
DEFAULT_MINUTE_CACHE_TIMEOUT = 5


@dataclass(frozen=True)
class ConfigKeys:
    CACHE_TIMEOUT = "cache_timeout"


class Plugin(PluginInstance, TriggerQueryHandler):
    _cached_items = None
    _last_fetch_time = 0

    iconUrls = [f"file:{Path(__file__).parent}/bw.svg"]

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

        self.cache_timeout = (
            self.readConfig(ConfigKeys.CACHE_TIMEOUT, int)
            or DEFAULT_MINUTE_CACHE_TIMEOUT
        )

    def defaultTrigger(self):
        return "bw "

    @property
    def cache_timeout(self):
        return int(self._cache_timeout / 60)

    @cache_timeout.setter
    def cache_timeout(self, value):
        self._cache_timeout = int(value * 60)
        self.writeConfig(ConfigKeys.CACHE_TIMEOUT, value)

    def configWidget(self):
        return [
            {
                "type": "label",
                "text": "Cache (result of `rbw list`) duration",
            },
            {
                "type": "spinbox",
                "property": ConfigKeys.CACHE_TIMEOUT,
                "label": f"Minutes: (max: {MAX_MINUTES_CACHE_TIMEOUT}, disable: 0)",
                "widget_properties": {"maximum": MAX_MINUTES_CACHE_TIMEOUT},
            },
        ]

    def handleTriggerQuery(self, query):
        results = []
        if query.string.strip().lower() == "sync":
            results.append(
                StandardItem(
                    id="sync",
                    text="Sync Bitwarden Vault",
                    iconUrls=self.iconUrls,
                    actions=[
                        Action(
                            id="sync",
                            text="Syncing Bitwarden Vault",
                            callable=lambda: self._sync_vault(),
                        )
                    ],
                )
            )

        for p in self._filter_items(query):
            results.append(
                StandardItem(
                    id=p["id"],
                    text=p["path"],
                    subtext=p["user"],
                    iconUrls=self.iconUrls,
                    actions=[
                        Action(
                            id="copy",
                            text="Copy password to clipboard",
                            callable=lambda item=p: self._password_to_clipboard(item),
                        ),
                        Action(
                            id="copy-auth",
                            text="Copy auth code to clipboard",
                            callable=lambda item=p: self._code_to_clipboard(item),
                        ),
                        Action(
                            id="copy-username",
                            text="Copy username to clipboard",
                            callable=lambda username=p["user"]: setClipboardText(
                                text=username
                            ),
                        ),
                        Action(
                            id="edit",
                            text="Edit entry in terminal",
                            callable=lambda item=p: self._edit_entry(item),
                        ),
                    ],
                )
            )

        query.add(results)

    def _get_items(self):
        not_first_time = self._cached_items is not None

        time_passed = time.time() - self._last_fetch_time
        is_chache_fresh = time_passed < self._cache_timeout

        if not_first_time and is_chache_fresh:
            return self._cached_items

        field_names = ["id", "name", "user", "folder"]
        raw_items = run(
            ["rbw", "list", "--fields", ",".join(field_names)],
            capture_output=True,
            encoding="utf-8",
            check=True,
        )

        items = []

        for line in raw_items.stdout.splitlines():
            fields = line.split("\t")
            item = dict(zip(field_names, fields))

            if item["folder"]:
                item["path"] = item["folder"] + "/" + item["name"]
            else:
                item["path"] = item["name"]

            items.append(item)

        self._cached_items = items
        self._last_fetch_time = time.time()

        return items

    def _filter_items(self, query):
        passwords = self._get_items() or []
        search_fields = ["path", "user"]
        # Use a set for faster membership tests
        words = set(query.string.strip().lower().split())

        filtered_passwords = []

        for p in passwords:
            match_all_words_with_any_field = all(
                any(word in p[field].lower() for field in search_fields)
                for word in words
            )

            if match_all_words_with_any_field:
                filtered_passwords.append(p)

        return filtered_passwords

    def _sync_vault(self):
        run(["rbw", "sync"], check=True)

        self._cached_items = None
        self._last_fetch_time = 0

    @staticmethod
    def _password_to_clipboard(item):
        rbw_id = item["id"]

        password = run(
            ["rbw", "get", rbw_id], capture_output=True, encoding="utf-8", check=True
        ).stdout.strip()

        setClipboardText(text=password)

    @staticmethod
    def _code_to_clipboard(item):
        rbw_id = item["id"]

        try:
            code = run(
                ["rbw", "code", rbw_id],
                capture_output=True,
                encoding="utf-8",
                check=True,
            ).stdout.strip()
        except CalledProcessError as err:
            code = run(
                ["echo", err.__str__()],
                capture_output=True,
                encoding="utf-8",
                check=True,
            ).stdout.strip()

        setClipboardText(text=code)

    @staticmethod
    def _edit_entry(item):
        rbw_id = item["id"]

        runTerminal(script=f"rbw edit {rbw_id}")
