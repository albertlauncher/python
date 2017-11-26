"""The extension finds out your internal and external ip address"""

from shutil import which
from albertv0 import *
import subprocess
import socket
import os


__iid__ = "PythonInterface/v0.1"
__prettyname__ = "IP Addresses"
__version__ = "1.0"
__trigger__ = "ip "
__author__ = "Benedict Dudel"
__dependencies__ = ["curl"]

if which("curl") is None:
    raise Exception("'curl' is not in $PATH.")

iconPath = iconLookup("preferences-system-network")


def handleQuery(query):
    if not query.isTriggered:
        return None

    proc = subprocess.run(["curl", "ipecho.net/plain"], stdout=subprocess.PIPE)
    externalIP = proc.stdout.decode("utf-8")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.255.255.255", 1))
    internalIP = s.getsockname()[0]
    s.close()

    items = []
    if externalIP:
        items.append(Item(
            id = __prettyname__,
            icon = iconPath,
            text = externalIP,
            subtext = "Your external ip address from ipecho.net",
            actions = [
                ClipAction("Copy ip address to clipboard", externalIP)
            ]
        ))

    if internalIP:
        items.append(Item(
            id = __prettyname__,
            icon = iconPath,
            text = internalIP,
            subtext = "Your internal ip address",
            actions = [
                ClipAction("Copy ip address to clipboard", internalIP)
            ]
        ))

    return items
