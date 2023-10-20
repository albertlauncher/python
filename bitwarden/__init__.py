# -*- coding: utf-8 -*-

from pathlib import Path
from subprocess import run, CalledProcessError

from albert import *

md_iid = '2.0'
md_version = "1.3"
md_name = "Bitwarden"
md_description = "'rbw' wrapper extension"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python"
md_maintainers = "@ovitor"
md_credits = "Original author: @tylio"
md_bin_dependencies = ["rbw"]


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_iid,
                                     name=md_name,
                                     description=md_description,
                                     defaultTrigger='bw ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/bw.svg"]


    def handleTriggerQuery(self, query):
        if query.string.strip().lower() == "unlock":
            query.add(
                StandardItem(
                    id="unlock",
                    text="Unlock Bitwarden Vault",
                    iconUrls=self.iconUrls,
                    actions=[
                        Action(
                            id="unlock",
                            text="Unlocking Bitwarden Vault",
                            callable=lambda: runTerminal(
                                script="rbw stop-agent && rbw unlock",
                                close_on_exit=True
                            )
                        )
                    ]
                )
            )

        filtered_items = self.__filter_items(query)

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
                            callable=lambda item=p: self.__get_password(item)
                        ),
                        Action(
                            id="copy-auth",
                            text="Copy auth code to clipboard",
                            callable=lambda item=p: self.__get_auth_code(item)
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
                            callable=lambda item=p: self.__edit_entry(item)
                        )
                    ]
                )
            )

    def __get_items(self):
        field_names = ["id", "name", "user", "folder"]
        p = run(
            ["rbw", "list", "--fields", ",".join(field_names)],
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
        passwords = []
        for l in p.stdout.splitlines():
            fields = l.split("\t")
            d = dict(zip(field_names, fields))
            if d["folder"]:
                d["path"] = d["folder"] + "/" + d["name"]
            else:
                d["path"] = d["name"]
            passwords.append(d)

        return passwords

    def __filter_items(self, query):
        passwords = self.__get_items()
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

    def __get_password(self, item):
        id = item["id"]

        password = run(
            ["rbw", "get", id],
            capture_output=True,
            encoding="utf-8",
            check=True
        ).stdout.strip()

        setClipboardText(text=password)

    def __get_auth_code(self, item):
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

    def __edit_entry(self, item):
        id = item["id"]

        runTerminal(
            script=f"rbw edit {id}",
            close_on_exit=True
        )
