#!/usr/bin/env python

"""Access Gnotes

Search, open, create and delete notes."""

from albertv0 import *
from dbus import SessionBus, Interface, DBusException
from shutil import which
from datetime import datetime
import re

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Gnote"
__version__ = "1.1"
__trigger__ = "gn "
__author__ = "Manuel Schneider"
__bin__ = __prettyname__.lower()
__dependencies__ = [__bin__, "python-dbus"]

BUS = "org.gnome.%s" % __prettyname__
OBJ = "/org/gnome/%s/RemoteControl" % __prettyname__
IFACE = 'org.gnome.%s.RemoteControl' % __prettyname__

if which(__bin__) is None:
    raise Exception("'%s' is not in $PATH." % __bin__)

iconPath = iconLookup(__bin__)


def handleQuery(query):
    results = []
    if query.isTriggered:
        try:
            if not SessionBus().name_has_owner(BUS):
                warning("Seems like %s is not running" % __bin__)
                return []

            obj = SessionBus().get_object(bus_name=BUS, object_path=OBJ)
            iface = Interface(obj, dbus_interface=IFACE)

            if query.string.strip():
                for note in iface.SearchNotes(query.string.lower(), False):
                    results.append(
                        Item(id="%s%s" % (__prettyname__, note),
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

                results.append(Item(id="%s-create" % __prettyname__,
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
