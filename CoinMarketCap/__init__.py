# -*- coding: utf-8 -*-

"""Shortcut to quickly show the stats of crypto currencies on CoinmMarketCap.com"""

from albertv0 import *
from urllib import request
import re
import os
import json

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "CoinMarketCap"
__version__ = "1.1"
__trigger__ = "cmc "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = os.path.dirname(__file__)+"/emblem-money.svg"
coins = None


def initialize():
    global coins
    req = request.Request("https://files.coinmarketcap.com/generated/search/quick_search.json")
    with request.urlopen(req) as response:
        coins = json.load(response)


def handleQuery(query):
    if not query.isTriggered:
        return

    stripped = query.string.strip().lower()
    items = []
    if stripped:
        pattern = re.compile(stripped, re.IGNORECASE)
        for coin in coins:
            name = coin['name']
            symbol = coin['symbol']
            if name.lower().startswith(stripped) or symbol.lower().startswith(stripped):
                items.append(Item(
                    id=__prettyname__,
                    icon=iconPath,
                    text="%s <i>(%s)</i>" % (pattern.sub(lambda m: "<u>%s</u>" % m.group(0), name),
                                      pattern.sub(lambda m: "<u>%s</u>" % m.group(0), symbol)),
                    subtext="#%s" % coin['rank'],
                    completion=query.rawString,
                    actions=[UrlAction("Show on CoinMarketCap website", "https://coinmarketcap.com/currencies/%s/" % coin['slug'])]
                ))
    else:
        for coin in coins:
            items.append(Item(
                id=__prettyname__,
                icon=iconPath,
                text="%s <i>(%s)</i>" % (coin['name'], coin['symbol']),
                subtext="#%s" % coin['rank'],
                completion=query.rawString,
                actions=[UrlAction("Show on CoinMarketCap website", "https://coinmarketcap.com/currencies/%s/" % coin['slug'])]
            ))
    return items
