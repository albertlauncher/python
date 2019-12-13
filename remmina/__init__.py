# -*- coding: utf-8 -*-

"""Search and start Remmina connections."""

from albertv0 import *
import os
import subprocess
from glob import glob
from re import search, IGNORECASE
import configparser

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Remmina"
__version__ = "0.1"
__trigger__ = "rm"
__author__ = "Oğuzcan Küçükbayrak"
__dependencies__ = []

iconPath = "%s/remmina.svg" % (os.path.dirname(__file__))
connectionsPath = "%s/.local/share/remmina" % (os.environ['HOME'])
protoIconPath = "/usr/share/icons/hicolor/scalable/emblems/remmina-%s-symbolic.svg"


def runRemmina(cf=""):
    args = (['remmina'], ['remmina', '-c', cf])[len(cf) > 0]
    subprocess.Popen(
        args,
        cwd=os.environ['HOME'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )


def searchConfigFiles(query):
    results = []
    files = [f for f in glob(connectionsPath + "**/*.remmina", recursive=True)]
    for f in files:
        conf = configparser.ConfigParser()
        conf.read(f)

        name = conf['remmina']['name']
        group = conf['remmina']['group']
        server = conf['remmina']['server']
        proto = conf['remmina']['protocol']
        if (search(query, name, IGNORECASE)):
            results.append(
                Item(
                    id=__prettyname__,
                    icon=protoIconPath % (proto.lower()),
                    text="%s/ %s" % (group, name),
                    subtext="%s %s" % (proto, server),
                    actions=[
                        FuncAction("Open connection",
                                   lambda cf=f: runRemmina(cf))
                    ]
                )
            )
    return results


def handleQuery(query):
    if query.isTriggered:
        stripped = query.string.strip()
        if stripped:
            results = searchConfigFiles(stripped)
            if results:
                return results

        return Item(
            id=__prettyname__,
            icon=iconPath,
            text=__prettyname__,
            subtext=__doc__,
            actions=[FuncAction("Open Remmina", runRemmina)]
        )
