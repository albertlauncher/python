# -*- coding: utf-8 -*-

from pathlib import Path
from subprocess import run, CalledProcessError

from albert import *

md_iid = '2.1'
md_version = "2.1"
md_name = "Bitwarden"
md_description = "'rbw' wrapper extension"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python"
md_authors = ["@ovitor", "@daviddeadly", "@manuelschneid3r"]
md_bin_dependencies = ["rbw"]


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     defaultTrigger='bw ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/bw.svg"]

    def handleTriggerQuery(self, query):
        if query.string.strip().lower() == "sync":
            query.add(
                StandardItem(
                    id="sync",
                    text="Sync Bitwarden Vault",
                    iconUrls=self.iconUrls,
                    actions=[
                        Action(
                            id="sync",
                            text="Syncing Bitwarden Vault",
                            callable=lambda: run(
                                ["rbw", "sync"],
                            )
                        )
                    ]
                )
            )

        filtered_items = self._filter_items(query)

        for p in filtered_items:
            query.add(
                StandardItem(
                    id=p["id"],
                    text=p["path"],
                    subtext=p["user"],
                    iconUrls=self.iconUrls,
                    actions=[
                        Action(
                            id="copy",
                            text="Copy password to clipboard",
                            callable=lambda item=p: self._password_to_clipboard(item)
                        ),
                        Action(
                            id="copy-auth",
                            text="Copy auth code to clipboard",
                            callable=lambda item=p: self._code_to_clipboard(item)
                        ),
                        Action(
                            id="copy-username",
                            text="Copy username to clipboard",
                            callable=lambda username=p["user"]:
                                setClipboardText(text=username)
                        ),
                        Action(
                            id="edit",
                            text="Edit entry in terminal",
                            callable=lambda item=p: self._edit_entry(item)
                        )
                    ]
                )
            )

    def _get_items(self):
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

        return items

    def _filter_items(self, query):
        passwords = self._get_items()
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

    def _password_to_clipboard(self, item):
        id = item["id"]

        password = run(
            ["rbw", "get", id],
            capture_output=True,
            encoding="utf-8",
            check=True
        ).stdout.strip()

        setClipboardText(text=password)

    def _code_to_clipboard(self, item):
        id = item["id"]

        try:
            code = run(
                ["rbw", "code", id],
                capture_output=True,
                encoding="utf-8",
                check=True
            ).stdout.strip()
        except CalledProcessError as err:
            code = run(
                ["echo", err.__str__()],
                capture_output=True,
                encoding="utf-8",
                check=True
            ).stdout.strip()

        setClipboardText(text=code)

    def _edit_entry(self, item):
        id = item["id"]

        runTerminal(
            script=f"rbw edit {id}",
            close_on_exit=True
        )
