"""Convert currencies.

Current backends: ECB, Yahoo.

Synopsis: <amount> <src currency> [to|as|in] <dest currency>
"""

import os
import re
import time
from urllib.request import urlopen
from xml.etree import ElementTree

from albert import *

md_iid = "0.5"
md_version = "2.0"
md_name = "Currency converter"
md_description = "Convert currencies using ECB/Yahoo"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/kill"
md_maintainers = "@Pete-Hamlin"
md_credits = "Original idea by Manuel Schneider"


class EuropeanCentralBank:

    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"

    def __init__(self):
        self.lastUpdate = 0
        self.exchange_rates = dict()
        self.name = "European Central Bank"

    def convert(self, amount, src, dst):
        if self.lastUpdate < time.time() - 10800:  # Update every 3 hours
            self.exchange_rates.clear()
            with urlopen(EuropeanCentralBank.url) as response:
                tree = ElementTree.fromstring(response.read().decode())
                for child in tree[2][0]:
                    curr = child.attrib["currency"]
                    rate = float(child.attrib["rate"])
                    self.exchange_rates[curr] = rate
                self.exchange_rates["EUR"] = 1.0  # For simpler algorithmic
                info("{}: Updated foreign exchange rates.".format(md_name))
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
        url = "https://search.yahoo.com/search?p={}+{}+to+{}".format(amount, src, dst)
        with urlopen(url) as response:
            html = response.read().decode()
            m = re.search("<span class=.*convert-to.*>(\d+(\.\d+)?)", html)
            if m:
                return m.group(1)


class Plugin(QueryHandler):
    icon_path = [
        "xdg:calculator",
        ":calc",
        os.path.dirname(__file__) + "/calc.svg",
    ]
    providers = [EuropeanCentralBank(), Yahoo()]
    regex = re.compile(r"(\d+\.?\d*)\s+(\w{3})(?:\s+(?:to|in|as))?\s+(\w{3})")

    def id(self):
        return __name__

    def name(self):
        return md_name

    def description(self):
        return md_description

    def initialize(self):
        pass

    def handleQuery(self, query):
        match = self.regex.fullmatch(query.string.strip())
        items = []
        if match:
            prep = (
                float(match.group(1)),
                match.group(2).upper(),
                match.group(3).upper(),
            )
            for provider in self.providers:
                result = provider.convert(*prep)
                if result:
                    items.append(
                        Item(
                            id="currency_convert",
                            text=result,
                            icon=self.icon_path,
                            subtext="Value of {} {} in {} (Source: {})".format(
                                *prep,
                                provider.name,
                            ),
                            actions=[
                                Action(
                                    "copy",
                                    "Copy to clipboard",
                                    lambda u=result: setClipboardText(u),
                                )
                            ],
                        )
                    )
                else:
                    warning(
                        "None of the foreign exchange rate providers came up with a result for %s"
                        % str(prep)
                    )
        query.add(items)
