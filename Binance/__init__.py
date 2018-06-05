# -*- coding: utf-8 -*-

"""Shortcut to quickly access the Binance markets

You can either search the items directly by typing the market name, e.g. xrpbtc, or list and filter
the markets by using the trigger and filter, e.g 'bnc [filter]'"""

from albertv0 import *
import time
import os
import urllib.request
import urllib.error
import json

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Binance"
__version__ = "1.2"
__trigger__ = "bnc "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = os.path.dirname(__file__) + "/%s.svg" % __name__
nextUpdate = 0
exchangeInfoUrl = "https://api.binance.com/api/v1/exchangeInfo"
tradeUrl = "https://www.binance.com/tradeDetail.html?symbol=%s_%s"
markets = []


class Market():
    def __init__(self, market, base):
        self.market = market
        self.base = base


def updateMarkets():
    # Update if older than an hour
    global nextUpdate
    if nextUpdate < time.time():
        try:
            global markets
            with urllib.request.urlopen(exchangeInfoUrl) as response:
                symbols = json.loads(response.read().decode())['symbols']
                markets.clear()
                for symbol in symbols:
                    # Skip this strange 123456 market
                    if symbol['baseAsset'] != "123":
                        markets.append(Market(market=symbol['baseAsset'],
                                              base=symbol['quoteAsset']))
            nextUpdate = time.time() + 3600
        except Exception as e:
            nextUpdate = time.time() + 60
            warning(e)


def makeItem(market):
    url = tradeUrl % (market.market, market.base)
    return Item(
        id="%s_%s%s" % (__prettyname__, market.market, market.base),
        icon=iconPath,
        text="%s/%s" % (market.market, market.base),
        subtext="Open the %s/%s market on binance.com" % (market.market, market.base),
        completion="%s%s%s" % (__trigger__, market.market, market.base),
        actions=[
            UrlAction("Show market in browser", url),
            ClipAction('Copy URL to clipboard', url)
        ]
    )


def handleQuery(query):

    updateMarkets()

    items = []
    stripped = query.string.strip().upper()

    if query.isTriggered:
        if stripped:
            for market in markets:
                if ("%s%s" % (market.market, market.base)).startswith(stripped):
                    items.append(makeItem(market))
        else:
            for market in markets:
                items.append(makeItem(market))
    else:
        for market in markets:
            if stripped and ("%s%s" % (market.market, market.base)).startswith(stripped):
                items.append(makeItem(market))

    return items
