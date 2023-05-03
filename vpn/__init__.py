from albert import *
from collections import namedtuple
import subprocess

md_iid = '1.0'
md_version = "1.3"
md_id = "vpn"
md_name = "VPN"
md_description = "Manage NetworkManager VPN connections"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python"
md_maintainers = ["@Bierchermuesli"]
md_credits = ["@janeklb"]
md_bin_dependencies = ["nmcli"]


class Plugin(TriggerQueryHandler):

    iconPath = ['xdg:network-wired']

    VPNConnection = namedtuple('VPNConnection', ['name', 'connected'])

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

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


    def buildItem(self,con):
        name = con.name
        command = 'down' if con.connected else 'up'
        text = f'Connect to {name}' if command == 'up' else f'Disconnect from {name}'
        commandline = ['nmcli', 'connection', command, 'id', name]
        return Item(
            id=f'vpn-{command}-{name}',
            text=name,
            subtext=text,
            icon=self.iconPath,
            completion=name,
            actions=[ Action("run",text=text, callable=lambda: runDetachedProcess(commandline)) ]
        )


    def handleTriggerQuery(self,query):
        if query.isValid:
            connections = self.getVPNConnections()
            if query.string:
                connections = [ con for con in connections if query.string.lower() in con.name.lower() ]
            query.add([ self.buildItem(con) for con in connections ])
