"""VPN Extension

Connect or disconnect from a network manager VPN profile"""


import subprocess
from collections import namedtuple
from albertv0 import *
from shutil import which


__iid__ = "PythonInterface/v0.2"
__prettyname__ = "VPN"
__version__ = "1.0"
__trigger__ = "vpn "
__author__ = "janeklb"
__dependencies__ = ['nmcli']


iconPath = iconLookup('network-wireless')
if not iconPath:
    iconPath = ":python_module"

VPNConnection = namedtuple('VPNConnection', ['name', 'connected'])


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
        icon=iconPath,
        completion=name,
        actions=[ ProcAction(text=text, commandline=commandline) ]
    )


def initialize():
    if which('nmcli') is None:
        raise Exception("'nmcli' is not in $PATH")


def handleQuery(query):
    if query.isValid and query.isTriggered:
        connections = getVPNConnections()
        if query.string:
            connections = [ con for con in connections if query.string.lower() in con.name.lower() ]
        return [ buildItem(con) for con in connections ]
    return []

