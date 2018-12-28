# -*- coding: utf-8 -*-

""""Search, open, create and delete Tomboy notes."""

import re
from datetime import datetime
from shutil import which

from dbus import DBusException, Interface, SessionBus

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Tomboy"
__version__ = "1.1"
__trigger__ = "tb "
__author__ = "Manuel Schneider"
__dependencies__ = ["tomboy", "python-dbus"]

BUS = "org.gnome.%s" % __prettyname__
OBJ = "/org/gnome/%s/RemoteControl" % __prettyname__
IFACE = 'org.gnome.%s.RemoteControl' % __prettyname__

cmd = __dependencies__[0]
if which(cmd) is None:
    raise Exception("'%s' is not in $PATH." % cmd)

iconPath = iconLookup(cmd)


def handleQuery(query):
    results = []
    if query.isTriggered:
        try:
            if not SessionBus().name_has_owner(BUS):
                warning("Seems like %s is not running" % cmd)
                return

            obj = SessionBus().get_object(bus_name=BUS, object_path=OBJ)
            iface = Interface(obj, dbus_interface=IFACE)

            if query.string.strip():
                for note in iface.SearchNotes(query.string.lower(), False):
                    results.append(
                        Item(id="%s%s" % (cmd, note),
                             icon=iconPath,
                             text=iface.GetNoteTitle(note),
                             subtext="%s%s" % ("".join(["#%s " % re.search('.+:.+:(.+)', s).group(1) for s in iface.GetTagsForNote(note)]),
                                               datetime.fromtimestamp(iface.GetNoteChangeDate(note)).strftime("Note from %c")),
                             completion=query.rawString,
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

                results.append(Item(id="%s-create" % cmd,
                                    icon=iconPath,
                                    text=__prettyname__,
                                    subtext="%s notes" % __prettyname__,
                                    completion=query.rawString,
                                    actions=[
                                        FuncAction("Open %s" % __prettyname__,
                                                   lambda: iface.DisplaySearch()),
                                        FuncAction("Create a new note", createAndShowNote)
                                    ]))
        except DBusException as e:
            critical(str(e))
    return results
