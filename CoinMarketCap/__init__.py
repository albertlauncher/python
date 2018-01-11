# -*- coding: utf-8 -*-

"""Query CoinmMarketCap.com"""

from albertv0 import *
from urllib import request, parse
import re
import os
import time
import json

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "CoinMarketCap"
__version__ = "1.0"
__trigger__ = "cmc "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = os.path.dirname(__file__)+"/emblem-money.svg"


def handleQuery(query):
    if not query.isTriggered:
        return

    time.sleep(0.2)
    if not query.isValid:
        info("saved time")
        return

    stripped = query.string.strip().lower()

    if stripped:
        url = "%s?%s" % ("https://api.coinmarketcap.com/v1/ticker/", parse.urlencode({'limit': 0}))
        req = request.Request(url)

        with request.urlopen(req) as response:
            items = []
            data = json.load(response)
            pattern = re.compile(query.string, re.IGNORECASE)
            for coindata in data:
                coinname = coindata['name']
                coincode = coindata['symbol']
                if coinname.lower().startswith(stripped) or coincode.lower().startswith(stripped):
                    # critical(coindata)
                    changes = [coindata['percent_change_1h'],
                               coindata['percent_change_24h'],
                               coindata['percent_change_7d']]
                    for idx, change in enumerate(changes):
                        if float(change) < 0:
                            changes[idx] = "<font color=\"red\">%s</font>" % change
                        elif float(change) > 0:
                            changes[idx] = "<font color=\"green\">%s</font>" % change
                    items.append(Item(
                        id=__prettyname__,
                        icon=iconPath,
                        text="%s <i>(%s/%s/%s)</i>" % (coindata['price_usd'], *changes),
                        subtext="%s <b>(%s)</b>" % (pattern.sub(lambda m: "<u>%s</u>" % m.group(0), coinname),
                                                    pattern.sub(lambda m: "<u>%s</u>" % m.group(0), coincode)),
                        completion=query.rawString,
                        actions=[UrlAction("Show on CoinMarketCap website", "https://coinmarketcap.com/currencies/%s/" % coinname)]
                    ))
            return items
    else:
        return Item(
            id=__prettyname__,
            icon=iconPath,
            text="CoinMarketCap",
            subtext="Enter a crypto currency you want to look up (…and wait. The API is slow.)",
            completion=query.rawString,
            actions=[UrlAction("Visit coinmarketcap.com", "https://coinmarketcap.com/")]
        )
