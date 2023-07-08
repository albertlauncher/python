import pathlib
import re
import subprocess
from collections import namedtuple

from albert import *

md_iid = "1.0"
md_version = "1.0"
md_id = "mullvad"
md_name = "Mullvad"
md_description = "Manage mullvad VPN connections"
md_license = "GPLv3"
md_url = "https://github.com/albertlauncher/python"
md_maintainers = ["@Pete-Hamlin"]
md_credits = ["@janeklb", "@Bierchermuesli"]
md_bin_dependencies = ["mullvad"]


class Plugin(TriggerQueryHandler):
    VPNConnection = namedtuple("VPNConnection", ["name", "connected"])

    def initialize(self):
        self.iconPath = ["xdg:network-wired"]
        self.connectIcon = str(pathlib.Path(__file__).parent / "lock-9.png")
        self.disconnectIcon = str(pathlib.Path(__file__).parent / "lock-1.png")
        self.reconnectIcon = str(pathlib.Path(__file__).parent / "lock-10.png")

        self.connection_regex = re.compile(r"[a-z]{2}-[a-z]*-[a-z]{2,4}-[\d]{2,3}")

    def id(self):
        return md_id

    def name(self):
        return md_name

    def defaultTrigger(self):
        return "mullvad "

    def description(self):
        return md_description

    def getRelays(self):
        relayStr = subprocess.check_output(
            "mullvad relay list", shell=True, encoding="UTF-8"
        )
        for relayStr in relayStr.splitlines():
            relay = relayStr.split()
            if relay and self.connection_regex.match(relay[0]):
                yield (relay[0], relayStr)

    def defaultItems(self):
        return [
            Item(
                id="connect",
                text="Connect",
                subtext="Connect to default server",
                icon=[self.connectIcon],
                actions=[
                    Action(
                        "connect",
                        "Connect",
                        lambda: runDetachedProcess(["mullvad", "connect"]),
                    )
                ],
            ),
            Item(
                id="disconnect",
                text="Disconnect",
                subtext="Disconnect from VPN",
                icon=[self.disconnectIcon],
                actions=[
                    Action(
                        "disconnect",
                        "Disconnect",
                        lambda: runDetachedProcess(["mullvad", "disconnect"]),
                    )
                ],
            ),
            Item(
                id="reconnect",
                text="Reconnect",
                subtext="Reconnect to current server",
                icon=[self.reconnectIcon],
                actions=[
                    Action(
                        "reconnect",
                        "Reconnect",
                        lambda: runDetachedProcess(["mullvad", "reconnect"]),
                    )
                ],
            ),
        ]

    def buildItem(self, relay):
        name = relay[0]
        command = ["mullvad", "relay", "set", "hostname", name]
        subtext = relay[1]
        return Item(
            id=f"vpn-{command}-{name}",
            text=name,
            subtext=subtext,
            icon=self.iconPath,
            completion=name,
            actions=[
                Action(
                    "connect",
                    text="Connect",
                    callable=lambda: runDetachedProcess(command),
                )
            ],
        )

    def handleTriggerQuery(self, query):
        if query.isValid:
            if query.string:
                relays = self.getRelays()
                query.add(
                    [
                        item
                        for item in self.defaultItems()
                        if query.string.lower() in item.text.lower()
                    ]
                )
                query.add(
                    [
                        self.buildItem(relay)
                        for relay in relays
                        if all(
                            q in relay[0].lower() for q in query.string.lower().split()
                        )
                    ]
                )
            else:
                query.add(self.defaultItems())
