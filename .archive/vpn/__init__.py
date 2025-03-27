# -*- coding: utf-8 -*-
# Copyright (c) 2020 janeklb
# Copyright (c) 2023 Bierchermuesli
# Copyright (c) 2020-2024 Manuel Schneider

import subprocess
from collections import namedtuple

from albert import *

md_iid = "3.0"
md_version = "2.0"
md_name = "VPN"
md_description = "Manage NetworkManager VPN connections"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/vpn"
md_authors = ["@janeklb", "@Bierchermuesli", "@manuelschneid3r"]
md_bin_dependencies = ["nmcli"]


class Plugin(PluginInstance, TriggerQueryHandler):

    VPNConnection = namedtuple('VPNConnection', ['name', 'connected'])

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

    def defaultTrigger(self):
        return "vpn "

    def getVPNConnections(self):
        consStr = subprocess.check_output(
            'nmcli -t connection show',
            shell=True,
            encoding='UTF-8'
        )
        for conStr in consStr.splitlines():
            con = conStr.split(':')
            if con[2] in ['vpn', 'wireguard']:
                yield self.VPNConnection(name=con[0], connected=con[3] != '')

    @staticmethod
    def buildItem(con):
        name = con.name
        command = 'down' if con.connected else 'up'
        text = f'Connect to {name}' if command == 'up' else f'Disconnect from {name}'
        commandline = ['nmcli', 'connection', command, 'id', name]
        return StandardItem(
            id=f'vpn-{command}-{name}',
            text=name,
            subtext=text,
            iconUrls=['xdg:network-wired'],
            inputActionText=name,
            actions=[Action("run", text=text, callable=lambda: runDetachedProcess(commandline))]
        )

    def handleTriggerQuery(self, query):
        if query.isValid:
            connections = self.getVPNConnections()
            if query.string:
                connections = [con for con in connections if query.string.lower() in con.name.lower()]
            query.add([self.buildItem(con) for con in connections])
