# -*- coding: utf-8 -*-

"""Open Remmina remote connections

Synopsis: <trigger> <query>"""

from albertv0 import *
import os
import configparser
from os.path import expanduser
from pathlib import Path


__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Remmina"
__version__ = "1.0"
__trigger__ = "re "
__author__ = "gentoo90"
__dependencies__ = ["remmina"]

REMMINA_ICON_PATH = iconLookup("org.remmina.Remmina")
PROTOCOL_ICONS = {
    "EXEC": iconLookup("remmina-tool-symbolic"),
    "NX": iconLookup("remmina-nx-symbolic"),
    "RDP": iconLookup("remmina-rdp-symbolic"),
    "SFTP": iconLookup("remmina-sftp-symbolic"),
    "SPICE": iconLookup("remmina-spice-symbolic"),
    "SSH": iconLookup("remmina-ssh-symbolic"),
    "VNC": iconLookup("remmina-vnc-symbolic"),
    "XDMCP": iconLookup("remmina-xdmcp-symbolic")
}
CONNECTIONS_PATH = Path("~/.local/share/remmina").expanduser()

connections = []


class RemminaConnectionItem(Item):
    def __init__(self, path):
        self.path = path

        conf = configparser.ConfigParser()
        conf.read(path)

        self.name = conf["remmina"]["name"]
        self.group = conf["remmina"]["group"]
        self.server = conf["remmina"]["server"]
        self.proto = conf["remmina"]["protocol"]

        super(RemminaConnectionItem, self).__init__(id=__prettyname__,
                    icon=PROTOCOL_ICONS.get(self.proto) or REMMINA_ICON_PATH,
                    text=f"{self.group}/ {self.name}" if len(self.group) > 0 else self.name,
                    subtext=f"{self.proto} {self.server}",
                    actions=[
                        ProcAction(text="Open",
                                   commandline=["remmina", "-c", str(self.path)],
                                   cwd="~")
                    ])

    def __repr__(self):
        return f"{self.text} ({self.path})"


def initialize():
    global connections
    connections = [RemminaConnectionItem(p) for p in CONNECTIONS_PATH.glob("*.remmina")]
    for c in connections:
        debug(f"Indexing Remmina connection: {c}")


def handleQuery(query):
    pattern = query.string.strip().lower()
    results = []
    try:
        for con in connections:
            if (pattern and pattern in con.text.lower() or not pattern and query.isTriggered):
                results.append(con)
    except Exception as e:
        critical(str(e))
    return results
