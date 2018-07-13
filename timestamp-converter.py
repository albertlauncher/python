# -*- coding: utf-8 -*-

"""
Convert timestamps to/from various formats to aide in software development.

Examples:
    # Current TS in millis since epoch converted to ISO format in UTC and local TZ
    ts 1531446783123     -->  2018-07-13 01:53:03.123 +0:00
                              2018-07-12 20:53:03.123 -5:00

    # Current TS in seconds since epoch (unix time) converted to ISO format in UTC and local TZ
    ts 1531446783        -->  2018-07-13 01:53:03.000 +0:00
                              2018-07-12 20:53:03.000 -5:00

    # Get the current TS in millis since epoch
    ts                   -->  1531446783123
"""

from albertv0 import *

from datetime import datetime
import time
import dateparser

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Timestamps"
__version__ = "1.0"
__trigger__ = "ts "
__author__ = "Matthew Bogner (matt@ibogner.net)"
__dependencies__ = ["dateparser"]

iconPath = iconLookup('edit-copy')

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def handleQuery(query):
    info("I'm in timestamp-converter.py")
    info("query.isTriggered: {0}".format(query.isTriggered))
    info("query.string: {0}".format(query.string))

    if not query.isTriggered:
        return

    if not query.string or query.string == "":
        # get current TS in millis since epoch
        millis = int(round(time.time() * 1000))
        utcTS = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        localTS = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        return [
            Item(
                id=str(millis),
                icon=iconPath,
                text=str(millis),
                subtext=str(millis),
                completion=str(millis),
                actions=[ClipAction('Copy TS to clipboard', str(millis))]
            ),
            Item(
                id=str(utcTS),
                icon=iconPath,
                text=str(utcTS),
                subtext=str(utcTS),
                completion=str(utcTS),
                actions=[ClipAction('Copy TS to clipboard', str(utcTS))]
            ),
            Item(
                id=str(localTS),
                icon=iconPath,
                text=str(localTS),
                subtext=str(localTS),
                completion=str(localTS),
                actions=[ClipAction('Copy TS to clipboard', str(localTS))]
            ),
        ]

    elif is_number(query.string):
        # if query.string is all numeric - it is millis or seconds since epoch.
        timestamp = int(query.string)
        if len(query.string) > 10:
            # this is millis
            timestamp = int(query.string) / 1000.0

        formattedDateUTC = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")
        formattedDateLocal = datetime.fromtimestamp(timestamp).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        return [
            Item(
                id=str(formattedDateUTC),
                icon=iconPath,
                text=str(formattedDateUTC),
                subtext=str(formattedDateUTC),
                completion=str(formattedDateUTC),
                actions=[ClipAction('Copy TS to clipboard', str(formattedDateUTC))]
            ),
            Item(
                id=str(formattedDateLocal),
                icon=iconPath,
                text=str(formattedDateLocal),
                subtext=str(formattedDateLocal),
                completion=str(formattedDateLocal),
                actions=[ClipAction('Copy TS to clipboard', str(formattedDateLocal))]
            ),
        ]

    else:
        # This is probably a formatted string.
        # TODO: how to utilize dateparser even when available on system default python install?
        dt = dateparser.parse(query.string)
        formattedDateUTC = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        return [
            Item(
                id=str(formattedDateUTC),
                icon=iconPath,
                text=str(formattedDateUTC),
                subtext=str(formattedDateUTC),
                completion=str(formattedDateUTC),
                actions=[ClipAction('Copy TS to clipboard', str(formattedDateUTC))]
            )
        ]
