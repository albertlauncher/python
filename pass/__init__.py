# -*- coding: utf-8 -*-

import fnmatch
import os
from albert import *

md_iid = '1.0'
md_version = "1.3"
md_name = "Pass"
md_description = "Manage passwords in pass"
md_bin_dependencies = ["pass"]
md_maintainers = "@maxmil"
md_license = "BSD-3"

HOME_DIR = os.environ["HOME"]
PASS_DIR = os.environ.get("PASSWORD_STORE_DIR", os.path.join(HOME_DIR, ".password-store/"))
ICON = ["xdg:dialog-password"]

class Plugin(TriggerQueryHandler):

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def synopsis(self):
        return "<pass-name>"

    def defaultTrigger(self):
        return "pass "

    def handleTriggerQuery(self, query):
        if query.string.strip().startswith("generate"):
            self.generatePassword(query)
        else: 
            self.showPasswords(query)

    def generatePassword(self, query):
        location = query.string.strip()[9:]

        query.add(Item(
            id="generate_password",
            icon=ICON,
            text="Generate a new password",
            subtext="The new password will be located at %s" % location,
            completion="pass %s" % query.string,
            actions=[
                Action("generate", "Generate", lambda: runDetachedProcess(["pass", "generate", "--clip", location, "20"]))
            ]
        ))

    def showPasswords(self, query):
        passwords = []
        if query.string.strip():
            passwords = self.getPasswordsFromSearch(query)
        else:
            passwords = self.getPasswords()

        results = []
        for password in passwords:
            name = password.split("/")[-1]
            results.append(
                Item(
                    id=password,
                    icon=ICON,
                    text=name,
                    subtext=password,
                    completion="pass %s" % password,
                    actions=[
                        Action("copy", "Copy", lambda pwd=password: runDetachedProcess(["pass", "--clip", pwd])),
                        Action("edit", "Edit", lambda pwd=password: runDetachedProcess(["pass", "edit", pwd])),
                        Action("remove", "Remove", lambda pwd=password: runDetachedProcess(["pass", "rm", "--force", pwd])),
                    ]
                ),
            )

        query.add(results)

    def getPasswords(self):
        passwords = []
        for root, dirnames, filenames in os.walk(PASS_DIR):
            for filename in fnmatch.filter(filenames, "*.gpg"):
                passwords.append(
                    os.path.join(root, filename.replace(".gpg", "")).replace(PASS_DIR, "")
                )

        return sorted(passwords, key=lambda s: s.lower())

    def getPasswordsFromSearch(self, query):
        passwords = []
        for password in self.getPasswords():
            if query.string.strip().lower() not in password.lower():
                continue

            passwords.append(password)

        return passwords
