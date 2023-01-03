# -*- coding: utf-8 -*-

"""Get internal and external IP address.

Synopsis: <trigger>"""

#  Copyright (c) 2022 Manuel Schneider

import socket
from urllib import request

from albert import *

__title__ = "IP Addresses"
__version__ = "0.4.0"
__triggers__ = "ip "
__authors__ = ["Manuel S.", "Benedict Dudel"]

iconPath = iconLookup("preferences-system-network")


def handleQuery(query):
    if not query.isTriggered:
        return None

    with request.urlopen("https://ipecho.net/plain") as response:
        externalIP = response.read().decode()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.255.255.255", 1))
    internalIP = s.getsockname()[0]
    s.close()

    items = []
    if externalIP:
        items.append(Item(
            id = __title__,
            icon = iconPath,
            text = externalIP,
            subtext = "Your external ip address from ipecho.net",
            actions = [ClipAction("Copy ip address to clipboard", externalIP)]
        ))

    if internalIP:
        items.append(Item(
            id = __title__,
            icon = iconPath,
            text = internalIP,
            subtext = "Your internal ip address",
            actions = [ClipAction("Copy ip address to clipboard", internalIP)]
        ))

    return items
