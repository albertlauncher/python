# -*- coding: utf-8 -*-
# Copyright (c) 2017 Benedict Dudel
# Copyright (c) 2023 Max
# Copyright (c) 2023 Pete-Hamlin

import fnmatch
import os
from albert import *

md_iid = '2.3'
md_version = "1.7"
md_name = "Pass"
md_description = "Manage passwords in pass"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/main/pass"
md_authors = ["@benedictdudel", "@maxmil", "@Pete-Hamlin"]
md_bin_dependencies = ["pass"]

HOME_DIR = os.environ["HOME"]
PASS_DIR = os.environ.get("PASSWORD_STORE_DIR", os.path.join(HOME_DIR, ".password-store/"))


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(
            self, self.id, self.name, self.description,
            synopsis='<pass-name>',
            defaultTrigger='pass '
        )
        self.iconUrls = ["xdg:dialog-password"]
        self._use_otp = self.readConfig("use_otp", bool) or False
        self._otp_glob = self.readConfig("otp_glob", str) or "*-otp.gpg"

    @property
    def use_otp(self):
        return self._use_otp

    @use_otp.setter
    def use_otp(self, value):
        print(f"Setting _use_otp to {value}")
        self._use_otp = value
        self.writeConfig("use_otp", value)

    @property
    def otp_glob(self):
        return self._otp_glob

    @otp_glob.setter
    def otp_glob(self, value):
        print(f"Setting _otp_glob to {value}")
        self._otp_glob = value
        self.writeConfig("otp_glob", value)

    def configWidget(self):
        return [
            {"type": "checkbox", "property": "use_otp", "label": "Enable pass OTP extension"},
            {
                "type": "lineedit",
                "property": "otp_glob",
                "label": "Glob pattern for OTP passwords",
                "widget_properties": {"placeholderText": "*-otp.gpg"},
            },
        ]

    def handleTriggerQuery(self, query):
        if query.string.strip().startswith("generate"):
            self.generatePassword(query)
        elif query.string.strip().startswith("otp") and self._use_otp:
            self.showOtp(query)
        else:
            self.showPasswords(query)

    def generatePassword(self, query):
        location = query.string.strip()[9:]

        query.add(
            StandardItem(
                id="generate_password",
                iconUrls=self.iconUrls,
                text="Generate a new password",
                subtext="The new password will be located at %s" % location,
                inputActionText="pass %s" % query.string,
                actions=[
                    Action(
                        "generate",
                        "Generate",
                        lambda: runDetachedProcess(["pass", "generate", "--clip", location, "20"]),
                    )
                ],
            )
        )

    def showOtp(self, query):
        otp_query = query.string.strip()[4:]
        passwords = []
        if otp_query:
            passwords = self.getPasswordsFromSearch(otp_query, otp=True)
        else:
            passwords = self.getPasswords(otp=True)

        results = []
        for password in passwords:
            results.append(
                StandardItem(
                    id=password,
                    iconUrls=self.iconUrls,
                    text=password.split("/")[-1],
                    subtext=password,
                    actions=[
                        Action(
                            "copy",
                            "Copy",
                            lambda pwd=password: runDetachedProcess(["pass", "otp", "--clip", pwd]),
                        ),
                    ],
                ),
            )
        query.add(results)

    def showPasswords(self, query):
        if query.string.strip():
            passwords = self.getPasswordsFromSearch(query.string)
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
                        Action(
                            "copy",
                            "Copy",
                            lambda pwd=password: runDetachedProcess(["pass", "--clip", pwd]),
                        ),
                        Action(
                            "edit",
                            "Edit",
                            lambda pwd=password: runDetachedProcess(["pass", "edit", pwd]),
                        ),
                        Action(
                            "remove",
                            "Remove",
                            lambda pwd=password: runDetachedProcess(["pass", "rm", "--force", pwd]),
                        ),
                    ],
                ),
            )

        query.add(results)

    def getPasswords(self, otp=False):
        passwords = []
        for root, dirnames, filenames in os.walk(PASS_DIR, followlinks=True):
            for filename in fnmatch.filter(filenames, self._otp_glob if otp else "*.gpg"):
                passwords.append(os.path.join(root, filename.replace(".gpg", "")).replace(PASS_DIR, ""))

        return sorted(passwords, key=lambda s: s.lower())

    def getPasswordsFromSearch(self, otp_query, otp=False):
        passwords = [password for password in self.getPasswords(otp) if otp_query.strip().lower() in password.lower()]
        return passwords
