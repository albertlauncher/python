# -*- coding: utf-8 -*-

import fnmatch
import os
from albert import *

md_iid = '2.0'
md_version = "1.4"
md_name = "Pass"
md_description = "Manage passwords in pass"
md_bin_dependencies = ["pass"]
md_maintainers = "@maxmil"
md_license = "BSD-3"

HOME_DIR = os.environ["HOME"]
PASS_DIR = os.environ.get("PASSWORD_STORE_DIR", os.path.join(HOME_DIR, ".password-store/"))


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis='<pass-name>',
                                     defaultTrigger='pass ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = ["xdg:dialog-password"]

    def handleTriggerQuery(self, query):
        if query.string.strip().startswith("generate"):
            self.generatePassword(query)
        else: 
            self.showPasswords(query)

    def generatePassword(self, query):
        location = query.string.strip()[9:]

        query.add(StandardItem(
            id="generate_password",
            iconUrls=self.iconUrls,
            text="Generate a new password",
            subtext="The new password will be located at %s" % location,
            inputActionText="pass %s" % query.string,
            actions=[
                Action("generate", "Generate", lambda: runDetachedProcess(["pass", "generate", "--clip", location, "20"]))
            ]
        ))

    def showPasswords(self, query):
        if query.string.strip():
            passwords = self.getPasswordsFromSearch(query)
        else:
            passwords = self.getPasswords()

        results = []
        for password in passwords:
            name = password.split("/")[-1]
            results.append(
                StandardItem(
                    id=password,
                    text=name,
                    subtext=password,
                    iconUrls=self.iconUrls,
                    inputActionText="pass %s" % password,
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
