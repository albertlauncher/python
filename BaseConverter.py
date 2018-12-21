# -*- coding: utf-8 -*-

"""Convert representations of numbers.
Usage: base <src base> <dest base> <number>
   Or: <src base name> <number> [padding]
Examples: base 10 16 1234567890
          dec 1024
          hex 5f 8"""

from albertv0 import *
import numpy as np

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Base Converter"
__version__ = "1.1"
__trigger__ = "base "
__author__ = "Manuel Schneider"
__dependencies__ = ["numpy"]

base_keywords = {"bin": 2, "oct": 8, "dec": 10, "hex": 16}

def buildItem(completion, src, dst, number, padding=0):
    item = Item(id=__prettyname__, completion=completion)
    try:
        src = int(src)
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
        if len(fields) == 3:
            return buildItem(query.rawString, fields[0], fields[1], fields[2])
        else:
            item = Item(id=__prettyname__, completion=query.rawString)
            item.text = __prettyname__
            item.subtext = "Enter a query in the form of \"&lt;srcbase&gt; &lt;dstbase&gt; &lt;number&gt;\""
            return item
    else:
        fields = query.string.split()
        if len(fields) < 2 or fields[0] not in base_keywords:
            return
        src = base_keywords[fields[0]]
        number = fields[1]
        padding = 0 if len(fields) < 3 else fields[2]
        results = []
        for dst in sorted(base_keywords.values()):
            if dst == src:
                continue
            results.append(buildItem(query.rawString, src, dst, number, padding))
        return results
