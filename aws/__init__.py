# -*- coding: utf-8 -*-

"""Query and open AWS Console Services.

Synopsis: <trigger> <query>"""

from yaml import dump, load, load_all
from os import path

from albertv0 import Item, UrlAction, iconLookup

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'AWS Console Services'
__version__ = '1.0'
__trigger__ = 'aws '
__author__ = 'Lucas Pearson'
__icon__ = path.dirname(__file__) + '/icons/aws.png'  # path.dirname(__file__) + '/icons/aws.png'

def handleQuery(query):
    if query.isTriggered and query.string.strip():
        fullpath = path.join(path.dirname(__file__), "console-services.yml")
        items = []
        with open(fullpath) as file:
            for service in load(file):
                if service["command"].startswith(query.string.strip()):
                    item = Item(id=__prettyname__,
                                icon=path.dirname(__file__) + '/icons/'+service["command"]+'.png',
                                text=service["command"],
                                subtext=service["description"],
                                completion=query.rawString,
                                actions=[ UrlAction('Show on AWS', service["url"]) ]
                    )
                    items.append(item)
        return items
