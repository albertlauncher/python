# -*- coding: utf-8 -*-

"""Shortcut to quickly access the Binance markets

You can either search the items directly by typing the market name, e.g. xrpbtc, or list and filter
the markets by using the trigger and filter, e.g 'bnc [filter]'"""

from albertv0 import *
import time
import os
from urllib import request
import json

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Binance"
__version__ = "1.0"
__trigger__ = "bnc "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = os.path.dirname(__file__) + "/%s.svg" % __name__
lastUpdate = 0
apiBaseUrl = "https://api.binance.com/"
tradeUrl = "https://www.binance.com/tradeDetail.html?symbol=%s_%s"
markets = []


class Market():
    def __init__(self, market, base, status):
        self.market = market
        self.base = base
        self.status = status


def updateMarkets():

    global markets
    req = request.Request(apiBaseUrl + "api/v1/exchangeInfo")
    with request.urlopen(req) as response:
        data = json.load(response)
        symbols = data['symbols']

        markets.clear()
        for symbol in symbols:

            # Skip this strage 123456 market
            if symbol['baseAsset'] == "123":
                continue

            markets.append(Market(market=symbol['baseAsset'],
                                  base=symbol['quoteAsset'],
                                  status=symbol['status']))


def makeItem(market):
    return Item(
        id="%s_%s%s" % (__prettyname__, market.market, market.base),
        icon=iconPath,
        text="%s/%s" % (market.market, market.base),
        subtext="Open the %s/%s market on binance.com" % (market.market, market.base),
        completion="%s%s%s" % (__trigger__, market.market, market.base),
        actions=[UrlAction("Show market in browser", tradeUrl % (market.market, market.base))]
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
