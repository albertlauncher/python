# -*- coding: utf-8 -*-

from albertv0 import *
import sqlite3
import re
import configparser, getpass,subprocess
import functools, itertools

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Firefox History"
__version__ = "1.0"
__trigger__ = "ff"
__author__ = "Harindu Dilshan"
__dependencies__ = []


def get_profile(username):
    config = configparser.ConfigParser()
    ini_path = "/home/{}/.mozilla/firefox/profiles.ini".format(username)
    config.read(ini_path)
    for profile in config:
        if 'Default' in config[profile] and config[profile]['Default'] == '1':
            return config[profile]['Path']

    return 'Profile0'

iconPath = iconLookup('firefox') or iconLookup('browser')

user = getpass.getuser()
profile = get_profile(user)
db_path = "/home/{}/.mozilla/firefox/{}/places.sqlite".format(user, profile)
history = []

def isEmpty(txt):
    if txt is None:
        return True
    elif len(txt.strip()) == 0:
        return True

    return False

def setupSession():
    conn = sqlite3.connect(db_path) 
    cursor = conn.cursor()
    query = 'select p.url,p.title from moz_historyvisits as h, moz_places as p where p.id == h.place_id order by h.visit_date desc;'
    query2 = 'select p.title from moz_historyvisits as h, moz_places as p where p.id == h.place_id order by h.visit_date desc;'
    results = (x for _, x in zip(range(1000), cursor.execute(query)))
    history = list(filter(lambda x: not isEmpty(x[1]), results))
    conn.close()
    
    return history

history = setupSession()

def concat(tuple_obj):
    text =''
    for item in tuple_obj:
        text += str(item)
    return text

def openInFirefox(cmds):
    subprocess.Popen(['firefox'] + cmds)

def handleQuery(query):
    pattern = re.compile(".*{}.*".format('.*'.join([re.escape( term )for term in query.string.split(' ')])), re.IGNORECASE)
    fields = query.string.split()
    searchItem = Item(id=__prettyname__,icon=iconPath,text="Search online '{}'".format(query.string),actions=[FuncAction("Search using Firefox",functools.partial(openInFirefox,['--search',query.string]))])
    results = []
    if len(query.string) >= 3:
        for line in history:
            item = Item(id=__prettyname__, icon=iconPath, completion=query.rawString)
            if(pattern.match(concat(line))):
                item.text = line[1]
                item.subtext = line[0]
                item.addAction(FuncAction("Open link in firefox",functools.partial(openInFirefox,[line[0]])))
                results.append(item)
        return [searchItem] + results
    else:
        return Item(id=__prettyname__,icon=iconPath,text="Type to search browser history")
