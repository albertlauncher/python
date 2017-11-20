from albertv0 import *
from subprocess import call, check_output
from shutil import which

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "VPN"
__version__ = "1.0"
__trigger__ = "v "
__author__ = "Raghuram Onti Srinivasan"
__dependencies__ = ['nmcli']


iconPath = iconLookup('network-wireless')
if not iconPath:
    iconPath = ":python_module"

if which('nmcli') is None:
    raise Exception("'nmcli' is not in $PATH.")

def handleQuery(query):
    if query.isTriggered:
        fields = query.string.split()
        item = Item(id=__prettyname__, icon=iconPath, completion=query.rawString)
        if len(fields) == 1:
            action = "up" if fields[0] == "on" else "down"
            out = check_output('nmcli con', shell=True)
            cli_map = {str(k):v for v,i,k in map(lambda x: x.split()[:3], out.splitlines())}
            if "b'vpn'" in cli_map:
                command = ["nmcli", "con", action,
                    cli_map["b'vpn'"], "--ask"]
                action = ProcAction(text="ProcAction",  commandline=command, cwd="~")
                item.addAction(action)
            return [item]
        else:
            item.text = __prettyname__
            item.subtext = "Enter a query in the form of on or off"
            return [item]
