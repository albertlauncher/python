# -*- coding: utf-8 -*-

"""Search, open, create and delete Tomboy notes.

Synopsis: <trigger> <filter>"""

#  Copyright (c) 2022 Manuel Schneider

import re
from datetime import datetime
from dbus import DBusException, Interface, SessionBus
from albert import *

__title__ = "Tomboy"
__version__ = "0.4.1"
__triggers__ = "tb "
__authors__ = "Manuel S."
__exec_deps__ = ["tomboy"]
__py_deps__ = ["dbus"]

BUS = "org.gnome.%s" % __title__
OBJ = "/org/gnome/%s/RemoteControl" % __title__
IFACE = 'org.gnome.%s.RemoteControl' % __title__
iconPath = iconLookup("tomboy")

def handleQuery(query):
    results = []
    if query.isTriggered:
        try:
            if not SessionBus().name_has_owner(BUS):
                warning("Seems like %s is not running" % __title__)
                return

            obj = SessionBus().get_object(bus_name=BUS, object_path=OBJ)
            iface = Interface(obj, dbus_interface=IFACE)

            if query.string.strip():
                for note in iface.SearchNotes(query.string.lower(), False):
                    results.append(
                        Item(id="%s%s" % (__title__, note),
                             icon=iconPath,
                             text=iface.GetNoteTitle(note),
                             subtext="%s%s" % ("".join(["#%s " % re.search('.+:.+:(.+)', s).group(1) for s in iface.GetTagsForNote(note)]),
                                               datetime.fromtimestamp(iface.GetNoteChangeDate(note)).strftime("Note from %c")),
                             actions=[
                                 FuncAction("Open note",
                                            lambda note=note: iface.DisplayNote(note)),
                                 FuncAction("Delete note",
                                            lambda note=note: iface.DeleteNote(note))
                                 ]))
            else:
                def createAndShowNote():
                    note = iface.CreateNote()
                    iface.DisplayNote(note)

                results.append(Item(id="%s-create" % __title__,
                                    icon=iconPath,
                                    text=__title__,
                                    subtext="%s notes" % __title__,
                                    actions=[
                                        FuncAction("Open %s" % __title__,
                                                   lambda: iface.DisplaySearch()),
                                        FuncAction("Create a new note", createAndShowNote)
                                    ]))
        except DBusException as e:
            critical(str(e))
    return results
