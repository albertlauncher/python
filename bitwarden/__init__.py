# -*- coding: utf-8 -*-

import os
from subprocess import run, CalledProcessError

from albert import *

md_iid = '1.0'
md_version = "1.2"
md_name = "Bitwarden"
md_description = "'rbw' wrapper extension"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python"
md_maintainers = "@ovitor"
md_credits = "Original author: @tylio"
md_bin_dependencies = ["rbw"]

class Plugin(TriggerQueryHandler):
    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "bw "

    def initialize(self):
        self.icon = [os.path.dirname(__file__) + "/bw.svg"]

    def _get_passwords(self):
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

    def handleTriggerQuery(self, query):
        if query.string.strip().lower() == "unlock":
            query.add(
                Item(
                    id="unlock",
                    text="Unlock Bitwarden Vault",
                    icon=self.icon,
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
        passwords = self._get_passwords()
        filtered_passwords = []
        search_fields = ["path", "user"]
        words = query.string.strip().lower().split()

        for p in passwords:
            all_matches = True
            for w in words:
                for k in search_fields:
                    if w in p[k].lower():
                        break
                else:
                    all_matches = False
                    break

            if all_matches:
                filtered_passwords.append(p)

        for p in filtered_passwords:
            pw = run(
                ["rbw", "get", p["id"]],
                capture_output=True,
                encoding="utf-8",
                check=True
            )
            try:
                code = run(
                    ["rbw", "code", p["id"]],
                    capture_output=True,
                    encoding="utf-8",
                    check=True
                )
            except CalledProcessError as err:
                code = run (["echo"], capture_output=True,encoding="utf-8", check=True)
            query.add(
                Item(
                    id=p["id"],
                    text=p["path"],
                    subtext=p["user"],
                    icon=self.icon,
                    actions=[
                        Action(
                            id="copy",
                            text="Copy password to clipboard",
                            callable=lambda password=pw.stdout.strip(): setClipboardText(
                                text=password)
                        ),
                        Action(
                            id="copy-auth",
                            text="Copy auth code to clipboard",
                            callable=lambda code=code.stdout.strip(): setClipboardText(
                                text=code)
                        ),
                        Action(
                            id="edit",
                            text="Edit entry in terminal",
                            callable=lambda pid=p['id']: runTerminal(
                                script=f"rbw edit {pid}",
                                workdir="~",
                                close_on_exit=False
                            )
                        )
                    ]
                )
            )