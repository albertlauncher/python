# -*- coding: utf-8 -*-

"""Open Gnome Terminal with selected profile."""

from albertv0 import *
from gi.repository import Gio
import os

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "GnomeTerminal"
__version__ = "1.0"
__trigger__ = "gt "
__author__ = "Stanislav Popov"
__dependencies__ = []

iconPath = os.path.dirname(__file__)+"/gnome-terminal.svg"


def handleQuery(query):
    if not query.isTriggered:
        return

    item = Item(id=__prettyname__, icon=iconPath, completion=query.rawString)

    if query.string.strip() == '':
        item.text = "Enter profile name"
        return item
    else:
        items = getProfileItems(query)
        if len(items) == 0:
            item.text = "Profile not found"
            return item
        return items


def getProfileItems(query):
    s = Gio.Settings(schema_id='org.gnome.Terminal.ProfilesList')
    profile_ids = s.get_value('list')

    profiles = []
    for profile_id in profile_ids:
        ps = Gio.Settings(
            schema_id='org.gnome.Terminal.Legacy.Profile',
            path='/org/gnome/terminal/legacy/profiles:/:%s/' % profile_id
        )
        profiles.append(ps.get_string('visible-name'))

    matched = [p for p in profiles if query.string in p]

    items = []
    for profile_name in matched:
        items.append(
            Item(
                id=__prettyname__,
                icon=iconPath,
                text=profile_name,
                actions=[
                    ProcAction(
                        text="Open terminal",
                        commandline=['gnome-terminal',
                                     '--window-with-profile', profile_name]
                    )
                ]
            )
        )
    return items
