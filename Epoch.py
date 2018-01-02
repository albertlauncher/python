# -*- coding: utf-8 -*-

"""Convert and get epoch"""

from albertv0 import *
import time

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Epoch Converter"
__version__ = "1.0"
__trigger__ = "ep "
__author__ = "Manuel Schneider"
__dependencies__ = []


def handleQuery(query):
    if query.isTriggered:
        fields = query.string.split()
        if not fields:
            timestamp = str(time.time())
            return Item(
                id=__prettyname__,
                text=timestamp,
                subtext="Current timestamp",
                completion=query.rawString,
                actions=[ClipAction("Copy timestamp to clipboard",
                                    timestamp)]
            )
        elif len(fields) == 1 and fields[0].isdigit():
            timestring = time.strftime("%c", time.localtime(int(fields[0])))
            return Item(
                id=__prettyname__,
                text=timestring,
                subtext="String representation of %s" % fields[0],
                completion=query.rawString,
                actions=[ClipAction("Copy result to clipboard",
                                    timestring)]
            )
        else:
            return Item(
                id=__prettyname__,
                text=__prettyname__,
                subtext="Invalid input. Argument must be empty or numeric.",
                completion=query.rawString
            )
