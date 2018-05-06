""" Passwordstore Extension """

import os
import fnmatch
from albertv0 import *
from shutil import which

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Pass"
__version__ = "1.0"
__trigger__ = "pass "
__author__ = "Benedict Dudel"
__dependencies__ = ["pass"]


if which("pass") is None:
    raise Exception("'pass' is not in $PATH.")

HOME_DIR = os.environ["HOME"]
PASS_DIR = os.environ.get("PASSWORD_STORE_DIR", os.path.join(HOME_DIR, ".password-store/"))
ICON_PATH = iconLookup("dialog-password")


def handleQuery(query):
    if query.isTriggered:
        if query.string.strip().startswith("generate"):
            return generatePassword(query)

        return showPasswords(query)

def generatePassword(query):
    location = query.string.strip()[9:]

    return [Item(
        id=__prettyname__,
        icon=ICON_PATH,
        text="Generate a new password",
        subtext="The new password will be located at %s" % location,
        completion="pass %s" % query.string,
        actions=[
            ProcAction("Generate", ["pass", "generate", "--clip", location, "20"])
        ]
    )]

def showPasswords(query):
    passwords = []
    if query.string.strip():
        passwords = getPasswordsFromSearch(query)
    else:
        passwords = getPasswords()

    results = []
    for password in passwords:
        name = password.split("/")[-1]
        results.append(
            Item(
                id=password,
                icon=ICON_PATH,
                text=name,
                subtext=password,
                completion="pass %s" % password,
                actions=[
                    ProcAction("Copy", ["pass", "--clip", password]),
                    ProcAction("Edit", ["pass", "edit", password]),
                    ProcAction("Remove", ["pass", "rm", "--force", password]),
                ]
            ),
        )

    return results

def getPasswords():
    passwords = []
    for root, dirnames, filenames in os.walk(PASS_DIR):
        for filename in fnmatch.filter(filenames, "*.gpg"):
            passwords.append(
                os.path.join(root, filename.replace(".gpg", "")).replace(PASS_DIR, "")
            )

    return sorted(passwords, key=lambda s: s.lower())

def getPasswordsFromSearch(query):
    passwords = []
    for password in getPasswords():
        if query.string.strip().lower() not in password.lower():
            continue

        passwords.append(password)

    return passwords
