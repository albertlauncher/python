# -*- coding: utf-8 -*-

"""Retrieve and convert datetime strings.

This extension provides items for 'time', 'date', 'datetime' and 'epoch' respectively 'unixtime'. \
The latter two yield the unix timestamp and also accept a unix timestamp as parameter which will \
be converted to a datetime string."""

import datetime
import time

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "DateTime"
__version__ = "1.0"
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = iconLookup('x-office-calendar')


def handleQuery(query):
    fields = list(filter(None, query.string.split()))
    if fields:
        def makeItem(text: str, subtext: str):
            return Item(
                id=__prettyname__,
                icon=iconPath,
                text=text,
                subtext=subtext,
                completion=query.rawString,
                actions=[ClipAction("Copy to clipboard", text)]
            )

        if "date".startswith(fields[0]) and len(fields) == 1:
            return makeItem(datetime.date.today().strftime("%x"),
                            "Current date")
        elif "time".startswith(fields[0]) and len(fields) == 1:
            return makeItem(datetime.datetime.now().strftime("%X"),
                            "Current time (local)")
        elif "utc".startswith(fields[0]) and len(fields) == 1:
            return makeItem(datetime.datetime.utcnow().strftime("%X"),
                            "Current time (UTC)")
        elif "datetime".startswith(fields[0]) and len(fields) == 1:
            return makeItem(datetime.datetime.now().strftime("%c"),
                            "Current date and time")
        elif "unixtime".startswith(fields[0]) or "epoch".startswith(fields[0]):
            if len(fields) == 2:
                if fields[1].isdigit():
                    return makeItem(time.strftime("%c", time.localtime(int(fields[1]))),
                                    "Date and time of '%s'" % fields[1])
                else:
                    return Item(
                        id=__prettyname__,
                        icon=iconPath,
                        text="Invalid input",
                        subtext="Argument must be empty or numeric.",
                        completion=query.rawString
                    )
            else:
                return makeItem(datetime.datetime.now().strftime("%s"),
                                "Current unixtime")
