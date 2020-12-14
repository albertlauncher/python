# -*- coding: utf-8 -*-

"""'rbw' wrapper extension."""

import fnmatch
import os
from shutil import which
from subprocess import run

from albert import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Bitwarden"
__version__ = "1.0"
__trigger__ = "bw "
__author__ = "Asger Hautop Drewsen"
__dependencies__ = ["rbw"]


if which("rbw") is None:
    raise Exception("'rbw' is not in $PATH.")

ICON_PATH = iconLookup("dialog-password")


def handleQuery(query):
    if not query.isTriggered:
        return

    passwords = get_passwords()
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

    results = []
    for p in filtered_passwords:
        results.append(
            Item(
                id=p["id"],
                icon=ICON_PATH,
                text=p["path"],
                subtext=p["user"],
                completion=f"rbw {p['path']}",
                actions=[
                    ProcAction(
                        "Copy",
                        [
                            "sh",
                            "-c",
                            f"rbw get {p['id']} | tr -d '\\n' | xclip -selection clipboard -in",
                        ],
                    ),
                    ProcAction(
                        "Copy auth code",
                        [
                            "sh",
                            "-c",
                            f"rbw code {p['id']} | tr -d '\\n' | xclip -selection clipboard -in",
                        ],
                    ),
                    TermAction("Edit", ["rbw", "edit", p["id"]]),
                ],
            ),
        )

    return results


def get_passwords():
    field_names = ["id", "name", "user", "folder"]
    p = run(
        ["rbw", "list", "--fields", *field_names],
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
