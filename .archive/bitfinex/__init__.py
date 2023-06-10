# -*- coding: utf-8 -*-

"""Access the Bitfinex markets.

Synopsis:
    filter
    <trigger> [filter]"""

from albert import *
import time
import os
import urllib.request
import urllib.error
import json
from collections import namedtuple
from threading import Thread, Event

__title__ = "BitFinex"
__version__ = "0.4.0"
__triggers__ = "bfx "
__authors__ = "Manuel S."

iconPath = os.path.dirname(__file__) + "/Bitfinex.svg"
symbolsEndpoint = "https://api.bitfinex.com/v1/symbols"
tradeUrl = "https://www.bitfinex.com/t/%s:%s"
markets = []
thread = None

Market = namedtuple("Market" , ["base", "quote"])

class UpdateThread(Thread):
    def __init__(self):
        super().__init__()
        self._stopevent = Event()

    def run(self):
        while True:
            global thread
            try:
                global markets
                with urllib.request.urlopen(symbolsEndpoint) as response:
                    symbols = json.loads(response.read().decode())
                    markets.clear()
                    for symbol in symbols:
                        symbol = symbol.upper()
                        markets.append(Market(base=symbol[0:3], quote=symbol[3:6]))
                    info("Bitfinex markets updated.")
                self._stopevent.wait(3600)  # Sleep 1h, wakeup on stop event
            except Exception as e:
                warning("Updating Bitfinex markets failed: %s" % str(e))
                self._stopevent.wait(60)  # Sleep 1 min, wakeup on stop event

            if self._stopevent.is_set():
                return

    def stop(self):
        self._stopevent.set()


def initialize():
    global thread
    thread = UpdateThread()
    thread.start()


def finalize():
    global thread
    if thread is not None:
        thread.stop()
        thread.join()

def makeItem(market):
    url = tradeUrl % (market.base, market.quote)
    return Item(
        id="%s_%s%s" % (__title__, market.base, market.quote),
        icon=iconPath,
        text="%s/%s" % (market.base, market.quote),
        subtext="Open the %s/%s market on bitfinex.com" % (market.base, market.quote),
        completion="%s%s%s" % (__triggers__, market.base, market.quote),
        actions=[
            UrlAction("Show market in browser", url),
            ClipAction('Copy URL to clipboard', url)
        ]
    )


def handleQuery(query):
    items = []
    stripped = query.string.strip().upper()

    if query.isTriggered:
        if stripped:
            for market in markets:
                if ("%s%s" % (market.base, market.quote)).startswith(stripped):
                    items.append(makeItem(market))
        else:
            for market in markets:
                items.append(makeItem(market))
    else:
        for market in markets:
            if stripped and ("%s%s" % (market.base, market.quote)).startswith(stripped):
                items.append(makeItem(market))

    return items
