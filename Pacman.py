"""Extension for the package manager `pacman`

The extension provides a way to install, remove and search for packages in the
archlinux.org database. To trigger the extension you just need to type `pacman `
in albert.

If no search query is supplied you have the option to do a system update.
Otherwise albert will try to search for packages with the search query within
the package name.

For more information about `pacman` please have a look at:
    - https://wiki.archlinux.org/index.php/pacman"""

from albertv0 import *
from shutil import which
import subprocess

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "PacMan"
__version__ = "1.1"
__trigger__ = "pacman "
__author__ = "Manuel Schneider, Benedict Dudel"
__dependencies__ = ["pacman", "expac"]


if which("pacman") is None:
    raise Exception("'pacman' is not in $PATH.")

iconPath = iconLookup("system-software-install")


def handleQuery(query):
    if query.isTriggered:
        if not query.string.strip():
            return Item(
                id="%s-update" % __prettyname__,
                icon=iconPath,
                text="Update all packages on the system",
                subtext="Synchronizes the repository databases and updates the system's packages",
                completion=__trigger__,
                actions=[TermAction("Update the system", ["sudo", "pacman", "-Syu"])]
            )

        items = []
        proc = subprocess.Popen(["expac", "-H", "M", "-Ss", "%n\n%v\n%r\n%d\n%u", query.string.strip()],
                                stdout=subprocess.PIPE)
        for line in proc.stdout:
            name = line.decode().rstrip()
            vers = proc.stdout.readline().decode().rstrip()
            repo = proc.stdout.readline().decode().rstrip()
            desc = proc.stdout.readline().decode().rstrip()
            purl = proc.stdout.readline().decode().rstrip()

            items.append(Item(
                id="%s%s%s" % (__prettyname__, repo, name),
                icon=iconPath,
                text="%s %s" % (name, vers),
                subtext="[%s] %s" % (repo, desc),
                completion="%s%s" % (query.trigger, name),
                actions=[
                    TermAction("Install", ["sudo", "pacman", "-S", name]),
                    TermAction("Remove", ["sudo", "pacman", "-Rs", name]),
                    UrlAction("Show on packages.archlinux.org",
                              "https://www.archlinux.org/packages/%s/x86_64/%s/" % (repo, name)),
                    UrlAction("Show project website", purl)
                ]
            ))

        if not items:
            return Item(
                id="%s-empty" % __prettyname__,
                icon=iconPath,
                text="Search on archlinux.org",
                subtext="No results found in the local database",
                completion=__trigger__,
                actions=[
                    UrlAction("Search on archlinux.org",
                              "https://www.archlinux.org/packages/?q=%s" % query.string.strip())
                ]
            )

        return items
