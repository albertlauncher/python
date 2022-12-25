"""Open Pidgin chats.

Matching contacts will be suggested.

Synopsis: <trigger> <filter>"""

#  Copyright (c) 2022 Manuel Schneider

import dbus

from albert import *

__title__ = "Pidgin"
__version__ = "0.4.0"
__authors__ = "Greizgh"
__triggers__ = "pidgin "
__exec_deps__ = ["python"]
__py_deps__ = ["dbus"]

iconPath = iconLookup("pidgin")
bus = dbus.SessionBus()


class ContactHandler:
    """Handle pidgin contact list"""

    _purple = None
    _contacts = []

    def __init__(self):
        self.refresh()

    def refresh(self):
        """Refresh both dbus connection and pidgin contact list"""
        try:
            self._contacts = []
            self._purple = bus.get_object(
                "im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject"
            )
            accounts = self._purple.PurpleAccountsGetAllActive()
            for account in accounts:
                buddies = self._purple.PurpleFindBuddies(account, "")
                for buddy in buddies:
                    # if purple.PurpleBuddyIsOnline(buddy):
                    name = self._purple.PurpleBuddyGetAlias(buddy)
                    self._contacts.append((name, account))
        except dbus.DBusException:
            critical("Could not connect to pidgin service")

    def isReady(self):
        """Check that this handler is ready to communicate"""
        return self._purple is not None

    def chatWith(self, account, name):
        """Open a pidgin chat window"""
        self._purple.PurpleConversationNew(1, account, name)

    def getMatch(self, query):
        """Get buddies matching query"""
        normalized = query.lower()
        return [item for item in self._contacts if normalized in item[0].lower()]


handler = ContactHandler()


def handleQuery(query):
    if not handler.isReady():
        handler.refresh()

    if query.isTriggered:
        target = query.string.strip()

        if target:
            items = []
            for match in handler.getMatch(target):
                items.append(
                    Item(
                        id=__title__,
                        icon=iconPath,
                        text="Chat with {}".format(match[0]),
                        subtext="Open a pidgin chat window",
                        completion=match[0],
                        actions=[
                            FuncAction(
                                "Open chat window",
                                lambda: handler.chatWith(match[1], match[0]),
                            )
                        ],
                    )
                )
            return items
