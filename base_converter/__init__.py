# -*- coding: utf-8 -*-

"""Convert representations of numbers.

Synopsis:
    <trigger> <dest base> <src>
    <number> [padding]

    where <src> is a literal of the form '0bXXX', '0XXX', or 0xXXX'."""

import numpy as np
from collections import defaultdict

from albertv0 import Item, ClipAction

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Base Converter"
__version__ = "2.0"
__trigger__ = "base "
__author__ = "Manuel Schneider"
__dependencies__ = ["numpy"]


class keyed_defaultdict(defaultdict):
    def __missing__(self, key):
        return self.default_factory(key)


base_prefixes = keyed_defaultdict(lambda k: 8 if k[0] == "0" and len(k) > 1 else 10)
base_prefixes["0b"] = 2
base_prefixes["0x"] = 16


def buildItem(completion, dst, number, padding=0):
    item = Item(id=__prettyname__, completion=completion)
    try:
        src = base_prefixes[number[:2]]
        dst = int(dst)
        padding = int(padding)
        integer = int(number, src)
        item.text = np.base_repr(integer, dst)
        if integer >= 0 and len(item.text) < padding:
            item.text = '0'*(padding-len(item.text)) + item.text
        item.subtext = "Base %s representation of %s (base %s)" % (dst, number, src)
        item.addAction(ClipAction("Copy to clipboard", item.text))
    except Exception as e:
        item.text = e.__class__.__name__
        item.subtext = str(e)
    return item


def handleQuery(query):
    if query.isTriggered:
        fields = query.string.split()
        if len(fields) == 2:
            return buildItem(query.rawString, fields[0], fields[1])
        else:
            item = Item(id=__prettyname__, completion=query.rawString)
            item.text = __prettyname__
            item.subtext = "Enter a query in the form of \"&lt;dstbase&gt; &lt;number&gt;\""
            return item
    else:
        fields = query.string.split()
        if len(fields) < 2:
            return
        src = base_prefixes[fields[:3]]
        number = fields[1]
        padding = 0 if len(fields) < 3 else fields[2]
        results = []
        for dst in sorted(base_prefixes.values().append(8)):
            if dst == src:
                continue
            results.append(buildItem(query.rawString, dst, number, padding))
        return results
