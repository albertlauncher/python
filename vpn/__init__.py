"""VPN Extension

Connect or disconnect from a network manager VPN profile"""


#  Copyright (c) 2022 Manuel Schneider

import subprocess
from collections import namedtuple
from albert import *


md_iid = "0.5"
md_version = "1.2"
md_name = "VPN"
md_description = "Plugin for VPN management"
md_license = "BSD-2"
md_url = "https://url.com/to/upstream/sources/and/maybe/issues"
md_maintainers = ["@janeklb","@uztnus"]
md_bin_dependencies = ["nmcli"]

# iconPath = iconLookup('network-wireless') or ":python_module"

VPNConnection = namedtuple('VPNConnection', ['name', 'connected'])

class Plugin(QueryHandler):
    def id(self):
        return __name__

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return 'vpn '

    def handleQuery(self, query):
        if query.isValid:
            connections = getVPNConnections()
            if query.string:
                connections = [ con for con in connections if query.string.lower() in con.name.lower() ]

            query.add([ buildItem(con) for con in connections ])


def getVPNConnections():
    consStr = subprocess.check_output(
        'nmcli -t connection show',
        shell=True,
        encoding='UTF-8'
    )
    for conStr in consStr.splitlines():
        con = conStr.split(':')
        if con[2] == 'vpn':
            yield VPNConnection(name=con[0], connected=con[3] != '')


def buildItem(con):
    name = con.name
    command = 'down' if con.connected else 'up'
    text = f'Connect to {name}' if command == 'up' else f'Disconnect from {name}'
    commandline = ['nmcli', 'connection', command, 'id', name]
    return Item(
        id=f'vpn-{command}-{name}',
        text=name,
        subtext=text,
        icon=[],
        completion=name,
        actions=[ Action(id=f"vpn-{command}-{name}",text=text, callable=lambda: runDetachedProcess(commandline)) ]
    )


