# -*- coding: utf-8 -*-

"""Convert currencies.

Current backends: ECB, Yahoo.

Synopsis: <amount> <src currency> [to|as|in] <dest currency>"""

#  Copyright (c) 2022 Manuel Schneider

import re
import time
from urllib.request import urlopen
from xml.etree import ElementTree

from albert import *

__title__ = "Currency converter"
__version__ = "0.4.0"
__authors__ = "Manuel S."

iconPath = iconLookup('accessories-calculator') or ":python_module"


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
                info("%s: Updated foreign exchange rates." % __title__)
                debug(str(self.exchange_rates))
            self.lastUpdate = time.time()

        if src in self.exchange_rates and dst in self.exchange_rates:
            src_rate = self.exchange_rates[src]
            dst_rate = self.exchange_rates[dst]
            return str(amount / src_rate * dst_rate)

class Yahoo:

    def __init__(self):
        self.name = "Yahoo"

    def convert(self, amount, src, dst):
        if amount.is_integer:
            amount = int(amount)
        url = 'https://search.yahoo.com/search?p=%s+%s+to+%s' % (amount, src, dst)
        with urlopen(url) as response:
            html = response.read().decode()
            m = re.search('<span class=.*convert-to.*>(\d+(\.\d+)?)', html)
            if m:
                return m.group(1)


providers = [EuropeanCentralBank(), Yahoo()]
regex = re.compile(r"(\d+\.?\d*)\s+(\w{3})(?:\s+(?:to|in|as))?\s+(\w{3})")

def handleQuery(query):
    match = regex.fullmatch(query.string.strip())
    if match:
        prep = (float(match.group(1)), match.group(2).upper(), match.group(3).upper())
        item = Item(id=__title__, icon=iconPath)
        for provider in providers:
            result = provider.convert(*prep)
            if result:
                item.text = result
                item.subtext = "Value of %s %s in %s (Source: %s)" % (*prep, provider.name)
                item.addAction(ClipAction("Copy result to clipboard", result))
                return item
        else:
            warning("None of the foreign exchange rate providers came up with a result for %s" % str(prep))
