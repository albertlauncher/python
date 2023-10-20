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
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     defaultTrigger='bw ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/bw.svg"]

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
                StandardItem(
                    id=p["id"],
                    text=p["path"],
                    subtext=p["user"],
                    iconUrls=self.iconUrls,
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
                            id="copy-username",
                            text="Copy username to clipboard",
                            callable=lambda username=p["user"]:
                                setClipboardText(text=username)
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