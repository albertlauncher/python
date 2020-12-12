# -*- coding: utf-8 -*-

"""Open Remmina remote connections

Synopsis: <trigger> <query>"""

from albertv0 import *
import os
from os.path import expanduser
from pathlib import Path


__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Remmina"
__version__ = "1.0"
__trigger__ = "re "
__author__ = "gentoo90"
__dependencies__ = ["remmina"]

remmina_icon_path = iconLookup("org.remmina.Remmina")

protocol_icons = {
    "EXEC": iconLookup("remmina-tool-symbolic"),
    "NX": iconLookup("remmina-nx-symbolic"),
    "RDP": iconLookup("remmina-rdp-symbolic"),
    "SFTP": iconLookup("remmina-sftp-symbolic"),
    "SPICE": iconLookup("remmina-spice-symbolic"),
    "SSH": iconLookup("remmina-ssh-symbolic"),
    "VNC": iconLookup("remmina-vnc-symbolic"),
    "XDMCP": iconLookup("remmina-xdmcp-symbolic")
}

connections = []


class RemminaConnection:
    def __init__(self, path):
        self.path = path
        self.name = str(self.path)
        self.icon = remmina_icon_path

        with open(self.path) as f:
            for l in f.readlines():
                if l.startswith("name"):
                    self.name = l.split("=")[1].strip()
                if l.startswith("protocol"):
                    protocol = l.split("=")[1].strip()
                    try:
                        self.icon = protocol_icons[protocol]
                    except KeyError:
                        pass

    def __repr__(self):
        return f"{self.name} ({self.path})"


def initialize():
    conf_dir = Path(expanduser("~/.remmina"))
    debug(f"CONF DIR: {conf_dir}")
    global connections
    connections = [RemminaConnection(p) for p in conf_dir.glob("*.remmina")]
    for c in connections:
        info(c)


def handleQuery(query):
    pattern = query.string.strip().lower()
    results = []
    try:
        for con in connections:
            if (pattern and pattern in con.name.lower() or not pattern and query.isTriggered):
                item = Item(id=__prettyname__,
                    icon=con.icon,
                    text=con.name,
                    actions=[
                        ProcAction(text="Open",
                                   commandline=["/usr/bin/remmina", "-c", str(con.path)],
                                   cwd="~")
                    ])
                results.append(item)
    except Exception as e:
        critical(str(e))
    return results
