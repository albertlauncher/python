"""Manage passwords.

This is a 'pass' wrapper extension.

Synopsis:
    <trigger> generate <location>
    <trigger> <filter>"""

import fnmatch
import os
from typing import List

from albert import *

md_iid = "0.5"
md_version = "1.0"
md_name = "Pass"
md_description = "Search/generate passwords from pass."
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/pass"
md_maintainers = "@Pete-Hamlin"
md_credits = "Original idea by Benedict Dudel"
md_bin_dependencies = "pass"


class Plugin(QueryHandler):
    home_dir = os.environ["HOME"]
    pass_dir = os.environ.get(
        "PASSWORD_STORE_DIR", os.path.join(home_dir, ".password-store/")
    )
    icon_path = "xdg:dialog-password"

    def id(self):
        return __name__

    def name(self):
        return md_name

    def description(self):
        return md_description

    def initialize(self):
        pass

    def handleQuery(self, query):
        if not query.isValid:
            return
        stripped = query.string.strip()
        passwords = self.get_passwords(stripped)
        results = []

        for password in passwords:
            name = password.split("/")[-1]
            results.append(
                Item(
                    id="pass",
                    text=name,
                    subtext=password,
                    icon=[self.icon_path],
                    actions=[
                        Action(
                            "copy",
                            "Copy password to clipboard",
                            lambda p=password: runDetachedProcess(["pass", "-c", p]),
                        ),
                        Action(
                            "edit",
                            "Edit password in terminal",
                            lambda p=password: runDetachedProcess(["pass", "edit", p]),
                        ),
                        Action(
                            "delete",
                            "Delete pass entry",
                            lambda p=password: runDetachedProcess(
                                ["pass", "rm", "--force", p]
                            ),
                        ),
                    ],
                )
            )
        query.add(results)

    def get_passwords(self, query_string) -> List[str]:
        passwords = []
        for root, _dirnames, filenames in os.walk(self.pass_dir):
            for filename in fnmatch.filter(filenames, "*.gpg"):
                passwords.append(
                    os.path.join(root, filename.replace(".gpg", "")).replace(
                        self.pass_dir, ""
                    )
                )
        # Filter by query string if it exists, otherwise return all
        if query_string:
            passwords = [k for k in passwords if query_string in k]
        return sorted(passwords, key=lambda s: s.lower())
