# -*- coding: utf-8 -*-

"""Shortcut to quickly access the Bitfinex markets

You can either search the items directly by typing the market name, e.g. xrpbtc, or list and filter
the markets by using the trigger and filter, e.g 'bfx [filter]'"""

from albertv0 import *
import time
import os
import urllib.request
import json

__iid__ = "PythonInterface/v0.1"
__prettyname__ = __name__
__version__ = "1.0"
__trigger__ = "bfx "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = os.path.dirname(__file__) + "/%s.svg" % __name__
lastUpdate = 0
symbolsEndpoint = "https://api.bitfinex.com/v1/symbols"
tradeUrl = "https://www.bitfinex.com/t/%s:%s"
markets = []


class Market():
    def __init__(self, base, quote):
        self.base = base
        self.quote = quote


def updateMarkets():
    global markets
    with urllib.request.urlopen(symbolsEndpoint) as response:
        symbols = json.loads(response.read().decode())
        markets.clear()
        for symbol in symbols:
            symbol = symbol.upper()
            markets.append(Market(base=symbol[0:3], quote=symbol[3:6]))


def makeItem(market):
    url = tradeUrl % (market.base, market.quote)
    return Item(
        id="%s_%s%s" % (__prettyname__, market.base, market.quote),
        icon=iconPath,
        text="%s/%s" % (market.base, market.quote),
        subtext="Open the %s/%s market on bitfinex.com" % (market.base, market.quote),
        completion="%s%s%s" % (__trigger__, market.base, market.quote),
        actions=[
            UrlAction("Show market in browser", url),
            ClipAction('Copy URL to clipboard', url)
        ]
    )


def handleQuery(query):

    # Update if older than an hour
    global lastUpdate
    now = time.time()
    if lastUpdate < now - 3600:
        lastUpdate = now
        updateMarkets()

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
