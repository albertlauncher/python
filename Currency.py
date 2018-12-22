# -*- coding: utf-8 -*-

"""Convert currencies.

Synopsis: <amount> <src currency> [to|as|in] <dest currency>"""

import json
import re
import time
from urllib.request import urlopen
from xml.etree import ElementTree

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Currency converter"
__version__ = "1.0"
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = iconLookup('accessories-calculator')
if not iconPath:
    iconPath = ":python_module"


class EuropeanCentralBank:

    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"

    def __init__(self):
        self.lastUpdate = 0
        self.exchange_rates = dict()
        self.name = "European Central Bank"

    def convert(self, amount, src, dst):
        if self.lastUpdate < time.time()-10800:  # Update every 3 hours
            self.exchange_rates.clear()
            with urlopen(EuropeanCentralBank.url) as response:
                tree = ElementTree.fromstring(response.read().decode())
                for child in tree[2][0]:
                    curr = child.attrib['currency']
                    rate = float(child.attrib['rate'])
                    self.exchange_rates[curr] = rate
                self.exchange_rates["EUR"] = 1.0  # For simpler algorithmic
                info("%s: Updated foreign exchange rates." % __prettyname__)
                debug(str(self.exchange_rates))
            self.lastUpdate = time.time()

        if src in self.exchange_rates and dst in self.exchange_rates:
            src_rate = self.exchange_rates[src]
            dst_rate = self.exchange_rates[dst]
            return str(amount / src_rate * dst_rate)

class Api:

    def __init__(self):
        self.name = "Currency Converter API"

    def convert(self, amount, src, dst):
        currency = '%s_%s' % (src, dst)
        url = 'http://free.currencyconverterapi.com/api/v5/convert?q=%s&compact=y' % (currency)
        with urlopen(url) as response:
            value = response.read().decode()
            result = json.loads(value)
            rate = result[currency]['val']
            return str(amount * float(rate))


providers = [EuropeanCentralBank(), Api()]
regex = re.compile(r"(\d+\.?\d*)\s+(\w{3})(?:\s+(?:to|in|as))?\s+(\w{3})")

def handleQuery(query):
    match = regex.fullmatch(query.string.strip())
    if match:
        prep = (float(match.group(1)), match.group(2).upper(), match.group(3).upper())
        item = Item(id=__prettyname__, icon=iconPath, completion=query.rawString)
        for provider in providers:
            result = provider.convert(*prep)
            if result:
                item.text = result
                item.subtext = "Value of %s %s in %s (Source: %s)" % (*prep, provider.name)
                item.addAction(ClipAction("Copy result to clipboard", result))
                return item
        else:
            warning("None of the foreign exchange rate providers came up with a result for %s" % str(prep))
    else:
        item = Item(id=__prettyname__, icon=iconPath, completion=query.rawString)
        item.text = __prettyname__
        item.subtext = "Enter a query in the form of \"&lt;amount&gt; &lt;src currency&gt; &lt;dst currency&gt;\""
        return item
