# -*- coding: utf-8 -*-

"""Conver currencies using Googgle finance. Example: exch 5 usd eur"""

from albertv0 import *
import urllib
import re

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Currency converter"
__version__ = "1.0"
__trigger__ = "exch "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = iconLookup('accessories-calculator')
if not iconPath:
    iconPath = ":python_module"


def handleQuery(query):
    if query.isTriggered:
        fields = query.string.split()
        item = Item(id=__prettyname__, icon=iconPath, completion=query.rawString)
        if len(fields) == 3:
            url = 'https://finance.google.com/finance/converter?a=%s&from=%s&to=%s' % tuple(fields)
            with urllib.request.urlopen(url) as response:
                html = response.read().decode("latin-1")
                m = re.search('<div id=currency_converter_result>.*<span class=bld>(\d+\.\d+).*</span>', html)
                if m:
                    result = m.group(1)
                    item.text = result
                    item.subtext = "Value of %s %s in %s" % tuple([x.upper() for x in fields])
                    item.addAction(ClipAction("Copy result to clipboard", result))
                    return item
                else:
                    item.text = "Error: HTTP reply does not contain a result"
                    item.subtext = "Maybe google finance changed their website"
                    return item
        else:
            item.text = __prettyname__
            item.subtext = "Enter a query in the form of <amount> <from> <to>"
            return item
