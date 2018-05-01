# -*- coding: utf-8 -*-

"""Convert currencies using Google Finance.
Usage: exch <amount> <src currency> <dest currency>
Example: exch 5 usd eur"""

from albertv0 import *
from urllib.request import urlopen
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
            url = 'https://search.yahoo.com/search?p=%s+%s+to+%s' % tuple(fields)
            with urlopen(url) as response:
                html = response.read().decode("latin-1")
                m = re.search('<span class=.*convert-to.*>(\d+(\.\d+)?)', html)
                if m:
                    result = m.group(1)
                    item.text = result
                    item.subtext = "Value of %s %s in %s" % tuple([x.upper() for x in fields])
                    item.addAction(ClipAction("Copy result to clipboard", result))
                    return item
                else:
                    item.text = "Error: HTTP reply does not contain a result"
                    item.subtext = "Maybe Google Finance changed their website"
                    return item
        else:
            item.text = __prettyname__
            item.subtext = "Enter a query in the form of &lt;amount&gt; &lt;from&gt; &lt;to&gt;"
            return item
