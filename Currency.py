# -*- coding: utf-8 -*-

"""Convert currencies using Yahoo Finance and XE.com.
Usage: exch <amount> <src currency> <dest currency>
Example: exch 5 usd eur"""

from albertv0 import *
import urllib
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
            urlGo = 'https://finance.google.com/finance/converter?a=%s&from=%s&to=%s' % tuple(fields)
            urlXE = 'https://www.xe.com/currencyconverter/convert/?Amount=%s&From=%s&To=%s' % tuple(fields)
            urlYa = 'https://search.yahoo.com/search?p=%s+%s+to+%s' % tuple(fields)
            urls = [urlYa, urlXE, urlGo]

            # Dictionary of URLs and their Regex expressions in the html.
            reDict = {
                urlGo: '<div id=currency_converter_result>.*<span class=bld>(\d+\.\d+).*</span>',
                urlXE: '<span class=\'uccResultAmount\'>(\d+\.\d+).*</span>',
                urlYa: '<span class=.*convert-to.*>(\d+(\.\d+)?)'
                }

            # Loop over the urls in the order of the list.
            # First one that doesn't except will return the function.
            for url in urls:
                try:
                    response = urlopen(url)
                    html = response.read().decode("latin-1")
                    m = re.search(reDict[url], html)
                except Exception as e:
                    response = None
                    m = None

                if m:
                    result = m.group(1)
                    item.text = result
                    item.subtext = "Value of %s %s in %s" % tuple([x.upper() for x in fields])
                    item.addAction(ClipAction("Copy result to clipboard", result))
                    return item

        else:
            item.text = __prettyname__
            item.subtext = "Enter a query in the form of &lt;amount&gt; &lt;from&gt; &lt;to&gt;"
            return item
