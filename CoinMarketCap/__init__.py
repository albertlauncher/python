# -*- coding: utf-8 -*-

"""Shortcut to quickly show the stats of crypto currencies on CoinmMarketCap.com"""

from albertv0 import *
from threading import Thread, Timer, Event
from urllib import request
from urllib.request import urlretrieve
import re
import os
from concurrent.futures import ThreadPoolExecutor

import json

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "CoinMarketCap"
__version__ = "1.2"
__trigger__ = "cmc "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = os.path.dirname(__file__)+"/emblem-money.svg"
cachePath = os.path.join(cacheLocation(), __name__)
thread = None
coins = None


class UpdateThread(Thread):
    def __init__(self):
        super().__init__()
        self._stopevent = Event()

    def run(self):
        global thread
        global coins

        while True:
            req = request.Request("https://files.coinmarketcap.com/generated/search/quick_search.json")
            with request.urlopen(req) as response:
                coins = json.load(response)

            if not os.path.isdir(cachePath):
                os.mkdir(cachePath)

            for coin in coins:
                if self._stopevent.is_set():
                    return
                filename = "%s.png" % coin['slug']
                url = "https://files.coinmarketcap.com/static/img/coins/128x128/%s" % filename
                filePath = os.path.join(cachePath, filename)
                executor = ThreadPoolExecutor(max_workers=40)
                if not os.path.isfile(filePath):
                    executor.submit(urlretrieve, url, filePath)
                executor.shutdown()

            self._stopevent.wait(10800)  # 3 hour
            if self._stopevent.is_set():
                return

    def stop(self):
        self._stop_event.set()


def initialize():
    thread = UpdateThread()
    thread.start()


def finalize():
    thread.join()


def handleQuery(query):
    if not query.isTriggered or coins is None:
        return

    stripped = query.string.strip().lower()
    items = []
    if stripped:
        pattern = re.compile(stripped, re.IGNORECASE)
        for coin in coins:
            name = coin['name']
            symbol = coin['symbol']
            if name.lower().startswith(stripped) or symbol.lower().startswith(stripped):
                coinIconPath = os.path.join(cachePath, "%s.png" % coin['slug'])
                items.append(Item(
                    id=__prettyname__,
                    icon=coinIconPath if os.path.isfile(coinIconPath) else iconPath,
                    text="%s <i>(%s)</i>" % (pattern.sub(lambda m: "<u>%s</u>" % m.group(0), name),
                                      pattern.sub(lambda m: "<u>%s</u>" % m.group(0), symbol)),
                    subtext="#%s" % coin['rank'],
                    completion=query.rawString,
                    actions=[UrlAction("Show on CoinMarketCap website", "https://coinmarketcap.com/currencies/%s/" % coin['slug'])]
                ))
    else:
        for coin in coins:
            coinIconPath = os.path.join(cachePath, "%s.png" % coin['slug'])
            items.append(Item(
                id=__prettyname__,
                icon=coinIconPath if os.path.isfile(coinIconPath) else iconPath,
                text="%s <i>(%s)</i>" % (coin['name'], coin['symbol']),
                subtext="#%s" % coin['rank'],
                completion=query.rawString,
                actions=[UrlAction("Show on CoinMarketCap website", "https://coinmarketcap.com/currencies/%s/" % coin['slug'])]
            ))
    return items
