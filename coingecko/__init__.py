# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

from albert import *
from time import time
from urllib import request
from json import load, loads, dumps
from pathlib import Path
from threading import Thread, Event

md_iid = "2.0"
md_version = "1.1"
md_name = "CoinGecko"
md_description = "Access CoinGecko"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/master/coingecko"
md_authors = "@manuelschneid3r"


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


class NameItem(StandardItem):
    def __init__(self,
                 identifier: str,
                 name: str,
                 symbol: str,
                 rank: int,
                 price: float,
                 cap: float,
                 vol: float,
                 change24h: float):
        StandardItem.__init__(
            self,
            id=identifier,
            text=f"{name} {price} {symbol}/$",
            subtext=f"#{rank}, 24h: {change24h}%, Cap: {cap:n} $, Vol: {vol:n} $",
            inputActionText=str(price),
            iconUrls=Plugin.iconUrls,
            actions=[
                Action("show", f"Show {name} on CoinGecko",
                       lambda id=identifier: openUrl(Plugin.coinsUrl + id)),
                Action("url", "Copy URL to clipboard",
                       lambda id=identifier: setClipboardText(Plugin.coinsUrl + id))
            ]
        )
        self.name = name
        self.symbol = symbol


class Plugin(PluginInstance, IndexQueryHandler):

    coinsUrl = "https://www.coingecko.com/en/coins/"
    iconUrls = [f"file:{Path(__file__).parent}/coingecko.png"]

    def __init__(self):
        IndexQueryHandler.__init__(
            self, md_id, md_name, md_description,
            defaultTrigger='cg ',
            synopsis='< symbol | name >'
        )
        PluginInstance.__init__(self, extensions=[self])

        self.items = []
        self.mtime = 0
        self.coinCacheFilePath = self.cacheLocation / "coins.json"
        self.thread = CoinFetcherThread(self.updateIndexItems, self.coinCacheFilePath)
        self.thread.start()

    def finalize(self):
        self.thread.stop()
        self.thread.join()

    def updateIndexItems(self):
        if self.coinCacheFilePath.is_file() and (mtime := self.coinCacheFilePath.lstat().st_mtime) > self.mtime:
            self.mtime = mtime
            with open(self.coinCacheFilePath) as f:
                self.items.clear()
                for json_object in load(f):
                    self.items.append(NameItem(
                        identifier=json_object['id'],
                        name=json_object['name'],
                        symbol=json_object['symbol'].upper(),
                        rank=json_object['market_cap_rank'],
                        price=json_object['current_price'],
                        cap=json_object['market_cap'],
                        vol=json_object['total_volume'],
                        change24h=json_object['price_change_percentage_24h']
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
