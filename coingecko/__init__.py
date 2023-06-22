# -*- coding: utf-8 -*-

"""Show and access crypto currencies on CoinGecko.com."""

from albert import *
from time import time
from urllib import request
from json import load, loads, dumps
from pathlib import Path
from threading import Thread, Event

md_iid = "1.0"
md_version = "1.0"
md_name = "CoinGecko"
md_description = "Access CoinGecko"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/coingecko"


class CoinFetcherThread(Thread):
    def __init__(self, callback, path: Path):
        super().__init__()
        self._stop_event = Event()
        self.callback = callback
        self.path = path

    def _fetchCoins(self):
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250"
        debug(f"Fetching data from {url}")
        try:
            response = request.urlopen(url, timeout=5)
            if response.getcode() == 200:
                json_data = loads(response.read().decode('utf-8'))
                with open(self.path, 'w') as f:
                    f.write(dumps(json_data))
            else:
                warning(f"Request failed with status code: {response.getcode()}")
        except Exception as e:
            warning(f"Request failed: {str(e)}")

    def run(self):
        while True:
            # update if older than 1h
            if not self.path.is_file() or (time() - self.path.lstat().st_mtime) > 3600:
                self._fetchCoins()
                self.callback()
            self._stop_event.wait(300)  # Check every 5 mins, wakeup on stop event
            if self._stop_event.is_set():
                return

    def stop(self):
        self._stop_event.set()


class CoinItem(AbstractItem):
    def __init__(self,
                 identifier: str,
                 name: str,
                 symbol: str,
                 rank: int,
                 price: float,
                 cap: float,
                 vol: float,
                 change24h: float):
        AbstractItem.__init__(self)
        self.identifier = identifier
        self.name = name
        self.symbol = symbol
        self.rank = rank
        self.price = price
        self.cap = cap
        self.vol = vol
        self.change24h = change24h

    def id(self):
        return self.identifier

    def text(self):
        return f"{self.name} {self.price} {self.symbol}/$"

    def subtext(self):
        return f"#{self.rank}, 24h: {self.change24h}%, Cap: {self.cap:n} $, Vol: {self.vol:n} $"

    def completion(self):
        return str(self.price)

    def icon(self):
        return [Plugin.iconPath]

    def actions(self):
        return [
            Action("show", f"Show {self.name} on CoinGecko",
                   lambda id=self.identifier: openUrl(Plugin.coinsUrl + id)),
            Action("url", "Copy URL to clipboard",
                   lambda id=self.identifier: setClipboardText(Plugin.coinsUrl + id))
        ]


class Plugin(IndexQueryHandler):
    iconPath = str(Path(__file__).parents[0] / "coingecko.png")
    coinsUrl = "https://www.coingecko.com/en/coins/"

    def initialize(self):
        self.items = []
        self.mtime = 0
        self.coinCacheFilePath = Path(self.cacheLocation()) / "coins.json"
        self.thread = CoinFetcherThread(self.updateIndexItems, self.coinCacheFilePath)
        self.thread.start()

    def finalize(self):
        self.thread.stop()
        self.thread.join()

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "cg "

    def updateIndexItems(self):
        mtime = self.coinCacheFilePath.lstat().st_mtime
        if self.coinCacheFilePath.is_file() and mtime > self.mtime:
            self.mtime = mtime
            with open(self.coinCacheFilePath) as f:
                self.items.clear()
                for json_object in load(f):
                    self.items.append(CoinItem(
                        identifier = json_object['id'],
                        name       = json_object['name'],
                        symbol     = json_object['symbol'].upper(),
                        rank       = json_object['market_cap_rank'],
                        price      = json_object['current_price'],
                        cap        = json_object['market_cap'],
                        vol        = json_object['total_volume'],
                        change24h  = json_object['price_change_percentage_24h']
                    ))

            index_items = []
            for item in self.items:
                index_items.append(IndexItem(item=item, string=item.name))
                index_items.append(IndexItem(item=item, string=item.symbol))
            self.setIndexItems(index_items)

    # override default trigger handling to sort by rank
    def handleTriggerQuery(self, query):
        qs = query.string.strip().lower()
        for item in self.items:
            if qs in item.name.lower() or qs in item.symbol.lower():
                query.add(item)
