# -*- coding: utf-8 -*-

"""Retrieve and convert datetime strings.

This extension provides items for 'time', 'date', 'datetime' and 'epoch' respectively 'unixtime'. \
The latter two yield the unix timestamp and also accept a unix timestamp as parameter which will \
be converted to a datetime string.

Synopsis:
    <time|date|datetime>
    <epoch|unixtime> [timestamp]"""

from datetime import datetime, date
import time

from albert import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "DateTime"
__version__ = "1.1"
__trigger__ = None
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
            return makeItem(date.today().strftime("%x"),
                            "Current date")
        elif "time".startswith(fields[0]) and len(fields) == 1:
            return makeItem(datetime.now().strftime("%X"),
                            "Current time (local)")
        elif "utc".startswith(fields[0]) and len(fields) == 1:
            return makeItem(datetime.utcnow().strftime("%X"),
                            "Current time (UTC)")
        elif "datetime".startswith(fields[0]) and len(fields) == 1:
            return makeItem(datetime.now().strftime("%c"),
                            "Current date and time")
        elif "unixtime".startswith(fields[0]) or "epoch".startswith(fields[0]) or "ts".startswith(fields[0]):
            if len(fields) == 2:
                if fields[1].isdigit():
                    timestamp = int(fields[1])
                    if len(fields[1]) > 10:
                        timestamp = timestamp / 1000

                    return [
                        makeItem(time.strftime("%c", time.localtime(timestamp)),
                                 "Date and time of '%s'" % fields[1]),
                        makeItem(datetime.fromtimestamp(timestamp).astimezone().strftime("%Y-%m-%d %H:%M:%S.%f %Z"),
                                 "Date and time of '%s'" % fields[1]),
                        makeItem(datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f UTC"),
                                 "UTC Date and time of '%s'" % fields[1])
                    ]
                else:
                    # TODO: how to utilize dateparser even when available on system default python install?
                    # dt = dateparser.parse(query.string)
                    return Item(
                        id=__prettyname__,
                        icon=iconPath,
                        text="Invalid input",
                        subtext="Argument must be empty or numeric.",
                        completion=query.rawString
                    )
            else:
                return [
                    makeItem(datetime.now().strftime("%s"),
                             "Current unixtime"),
                    makeItem(str(round(time.time() * 1000)),
                             "Millis since Epoch"),
                    makeItem(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f UTC"),
                             "UTC timestamp"),
                    makeItem(datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S.%f %Z"),
                             "Local timestamp")
                ]
