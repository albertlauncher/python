#!/usr/bin/env python

"""Access Gnotes

Search, open, create and delete notes."""

from albertv0 import *
from dbus import SessionBus, Interface
from shutil import which
from datetime import datetime

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Gnote"
__version__ = "1.0"
__trigger__ = "gn "
__author__ = "Manuel Schneider"
__bin__ = __prettyname__.lower()
__dependencies__ = [__bin__, "python-dbus"]

if which(__bin__) is None:
    raise Exception("'%s' is not in $PATH." % __bin__)


def initialize():
    global dbus, iconPath
    obj = SessionBus().get_object("org.gnome.%s" % __prettyname__,
                                  "/org/gnome/%s/RemoteControl" % __prettyname__)
    dbus = Interface(obj, dbus_interface='org.gnome.%s.RemoteControl' % __prettyname__)
    iconPath = iconLookup(__bin__)


def handleQuery(query):
    results = []
    if query.isTriggered:
        if query.string.strip():
            for note in dbus.SearchNotes(query.string.lower(), False):
                results.append(Item(id="%s%s" % (__prettyname__, note),
                                    icon=iconPath,
                                    text=dbus.GetNoteTitle(note),
                                    subtext=datetime.fromtimestamp(dbus.GetNoteChangeDate(note)).strftime("Note from %c"),
                                    completion=query.rawString,
                                    actions=[
                                        FuncAction("Open note",
                                                   lambda note=note: dbus.DisplayNote(note)),
                                        FuncAction("Delete note",
                                                   lambda note=note: dbus.DeleteNote(note))
                                    ]))
        else:
            def createAndShowNote():
                note = dbus.CreateNote()
                dbus.DisplayNote(note)

            results.append(Item(id="%s-create" % __prettyname__,
                                icon=iconPath,
                                text=__prettyname__,
                                subtext="%s notes" % __prettyname__,
                                completion=query.rawString,
                                actions=[
                                    FuncAction("Open %s" % __prettyname__,
                                               lambda: dbus.DisplaySearch()),
                                    FuncAction("Create a new note", createAndShowNote)
                                ]))
    return results
