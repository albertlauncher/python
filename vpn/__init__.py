"""VPN Extension

Connect or disconnect from a network manager VPN profile"""


from albert import *
from collections import namedtuple
import subprocess

md_iid = "0.5"
md_version = "0.5"
md_id = "vpn"
md_name = "VPN"
md_description = "Manages VPN (via nmcli)"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python"
md_maintainers = ["@Bierchermuesli"]
md_authors = ["@janeklb"]
md_lib_dependencies = ["nmcli"]



class Plugin(QueryHandler):

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
            if con[2] == 'vpn':
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


    def handleQuery(self,query):
        if query.isValid:
            connections = self.getVPNConnections()
            if query.string:
                connections = [ con for con in connections if query.string.lower() in con.name.lower() ]
            query.add([ self.buildItem(con) for con in connections ])
