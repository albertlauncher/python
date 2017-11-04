""" SSH """

import subprocess
import getpass
from albertv0 import *
from shutil import which
from pathlib import Path

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "SSH"
__version__ = "1.0"
__trigger__ = "ssh "
__author__ = "Benedict Dudel"
__dependencies__ = ["ssh"]

if which("ssh") is None:
    raise Exception("'ssh' is not in $PATH.")

iconPath = iconLookup('ssh')

def handleQuery(query):
    if query.isTriggered:
        hosts = {}
        hosts = getHostEntriesFromConfig(hosts)
        hosts = getHostEntriesFromHostsFile(hosts)

        items = []
        for key, host in hosts.items():
            if query.string and not query.string in host['host']:
                continue;

            item = Item(
                id=__prettyname__,
                icon=iconPath,
                text=host['host'],
                subtext=getSSHUrl(host['hostname'], host['port'], host['user']),
                completion='ssh %s' % host['host'],
                actions=[
                    UrlAction(
                        text="Open",
                        url=getSSHUrl(host['hostname'], host['port'], host['user'])
                    ),
                    TermAction(
                        text="Ping",
                        commandline=["ping", host['hostname']]
                    )
                ]
            )
            items.append(item)

        return items

def getHostEntriesFromConfig(hosts):
    home = str(Path.home())
    with open('%s/.ssh/config' % home, 'r') as file:
        currentHost = ''
        for line in file:
            line = line.strip()

            if not line:
                continue

            if line.startswith('Host') and not line.startswith('HostName'):
                currentHost = line[5:]
                hosts[currentHost] = {
                    'host': currentHost,
                    'hostname': currentHost,
                    'user': getpass.getuser(),
                    'port': 22
                }

            if not currentHost:
                continue

            if line.startswith('HostName'):
                hosts[currentHost]['hostname'] = line[9:]

            if line.startswith('User'):
                hosts[currentHost]['user'] = line[5:]

            if line.startswith('Port'):
                hosts[currentHost]['port'] = line[5:]

    return hosts

def getHostEntriesFromHostsFile(hosts):
    with open('/etc/hosts', 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            host = line.split()[1:][0]
            hosts[host] = {
                'host': host,
                'hostname': host,
                'user': getpass.getuser(),
                'port': 22
            }

    return hosts

def getSSHUrl(host, port, user):
    url = 'ssh://'
    if not user == getpass.getuser():
        url += '%s@' % user

    url += host
    if not port == 22:
        url += ':%s' % port

    return url
