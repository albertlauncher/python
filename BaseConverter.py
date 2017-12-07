# -*- coding: utf-8 -*-

"""Convert representations of numbers.
Usage: base <src base> <dest base> <number>
Example: base 10 16 1234567890"""

from albertv0 import *
import numpy as np

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Base Converter"
__version__ = "1.0"
__trigger__ = "base "
__author__ = "Manuel Schneider"
__dependencies__ = ["numpy"]


def handleQuery(query):
    if query.isTriggered:
        fields = query.string.split()
        item = Item(id=__prettyname__, completion=query.rawString)
        if len(fields) == 3:
            try:
                src = int(fields[0])
                dst = int(fields[1])
                number = fields[2]
                item.text = np.base_repr(int(number, src), dst)
                item.subtext = "Base %s representation of %s (base %s)" % (dst, number, src)
                item.addAction(ClipAction("Copy to clipboard", item.text))
            except Exception as e:
                item.text = e.__class__.__name__
                item.subtext = str(e)
            return item
        else:
            item.text = __prettyname__
            item.subtext = "Enter a query in the form of <srcbase> <dstbase> <number>"
            return item
