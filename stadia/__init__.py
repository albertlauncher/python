# -*- coding: utf-8 -*-

"""Stadia integration for albert launcher.

This extension adds the Stadia launch functions to the albert launcher, launch \
your favorite Stadia games scripts using stadia play <game name> quickly open chrome to \
the appropriate stadia page in google chrome

Synopsis: stadia [play|store] <game name>"""

from albertv0 import *
import os
from time import sleep
import webbrowser


__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Stadia game Launch"
__version__ = "1.0"
__trigger__ = "stadia "
__author__ = "Sam Sebastian"
__dependencies__ = []

iconPath = os.path.dirname(__file__)+"/stadia.svg"
gameIconPath = os.path.dirname(__file__)+"/icons/"

game_list = []
baseurl = "https://stadia.google.com/"
chrome_path = "/usr/bin/google-chrome"


# Can be omitted
def initialize():
    fetch_game_list()
    pass

def fetch_game_list():
    with open(os.path.dirname(__file__)+"/stadiapython.txt") as f:
        for line in f:
            game_list.append(line.strip().split(","))

# Can be omitted
def finalize():
    pass


def handleQuery(query):
    if not query.isTriggered:
        return

    # Note that when storing a reference to query, e.g. in a closure, you must not use
    # query.isValid. Apart from the query beeing invalid anyway it will crash the appplication.
    # The Python type holds a pointer to the C++ type used for isValid(). The C++ type will be
    # deleted when the query is finished. Therfore getting isValid will result in a SEGFAULT.

    # if query.string.startswith("run"):
    #     return Item(id=__prettyname__,
    #                 icon=os.path.dirname(__file__)+"/autokey.svg",
    #                 text="Run a script",
    #                 subtext="Run script: "+query.string)
        

    # if query.string.startswith("open"):
    #     raise ValueError('EXPLICITLY REQUESTED TEST EXCEPTION!')

    info(query.string)
    info(query.rawString)
    info(query.trigger)
    info(str(query.isTriggered))
    info(str(query.isValid))
    info(iconPath)


    critical(query.string)
    warning(query.string)
    debug(query.string)
    debug(query.string)

    results = []

    if query.string.startswith("play"):
        # print("play")
        for item in game_list:
            item_name = item[0]
            item_sku = item[1]
            item_app = item[2]
            item_icon_name = item[3]
            if query.string[5:].lower() in item_name.lower():
                ret_item = build_item_play(item_name,item_sku, item_app, item_icon_name)
                results.append(ret_item)

    if query.string.startswith("store"):
        for item in game_list:
            item_name = item[0]
            item_sku = item[1]
            item_app = item[2]
            item_icon_name = item[3]
            if query.string[6:].lower() in item_name.lower():
                ret_item = build_item_store(item_name,item_sku, item_app, item_icon_name)
                results.append(ret_item)
    # Api v 0.2
    info(configLocation())
    info(cacheLocation())
    info(dataLocation())

    return results

def build_item_play(name, sku, app, icon):
    item = Item()
    item.icon = gameIconPath+icon
    info(gameIconPath+icon)
    item.text = 'Launch %s in Stadia' % name
    item.subtext = 'Launch Game in Stadia %s' % name
    item.completion = __trigger__ + name
    def run_script():
        webbrowser.get(chrome_path).open(baseurl+"player/"+app)
    item.addAction(FuncAction("Run "+name, run_script))
    return item

def build_item_store(name,sku,app, icon):
    #https://stadia.google.com/store/details/377f50584071472096bcda89b0839bc3rcp1/sku/5dfb26075986434a9c7d99d0d55e0634
    item = Item()
    item.icon = gameIconPath+icon
    item.text = 'Open %s Store Page' % name
    item.subtext = 'Open %s Store Page' % name
    item.completion = __trigger__ + name
    def run_script():
        webbrowser.get(chrome_path).open(baseurl+"store/details/"+app+"/sku/"+sku)
    item.addAction(FuncAction("Run "+name, run_script))
    return item