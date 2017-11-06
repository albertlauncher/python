from albertv0 import *
from subprocess import call, check_output

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "VPN"
__version__ = "1.0"
__trigger__ = "v "
__author__ = "Raghuram Onti Srinivasan"
__dependencies__ = []


iconPath = iconLookup('config-language')
if not iconPath:
    iconPath = ":python_module"

def handleQuery(query):
    if query.isTriggered:
        fields = query.string.split()
        item = Item(id=__prettyname__, icon=iconPath, completion=query.rawString)
        if len(fields) == 1:
            action = "up" if fields[0] == "on" else "down"
            out = check_output('nmcli con', shell=True)
            cli_map = {k:v for v,i,k in map(lambda x: x.split()[:3], out.splitlines())}
            if "vpn" in cli_map:
                call(["nmcli", "con", action,
                    cli_map["vpn"], "--ask"])
            return [item]
        else:
            return [item]
