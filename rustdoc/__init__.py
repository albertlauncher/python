# -*- coding: utf-8 -*-

"""Search Rust crate documentations

An extension for searching through the rust documentation on `docs.rs`.

Usage:
    rustdoc <crate>
    rustdoc <crate>|std <query>"""

import os
import time
import json
import re
import requests as req
from py_mini_racer import py_mini_racer
from pyquery import PyQuery as pq

from albertv0 import *

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "RustDoc"
__version__ = "0.1.0"
__author__ = "succcubbus"
__trigger__ = "rustdoc "
__dependencies__ = ["requests", "py_mini_racer"]

path = os.path.dirname(__file__)
rustIcon = path + "/rust.png"
typeIcons = {
    'fn': path + "/fn.png"
}

def extractCrateInfo(crateEntry):
    description = crateEntry.find('.description').text().strip()
    releaseParts = crateEntry.find('.release').attr.href.split('/')
    if releaseParts[1] == 'crate':
        releaseParts.pop(0)
    return {
        'name': releaseParts[1],
        'version': releaseParts[2],
        'description': description
    }

def searchCrate(query):
    resultsPage = req.get(f'https://docs.rs/releases/search?query={query}')
    d = pq(resultsPage.text)
    crateList = d('.recent-releases-container > ul li').items()
    return map(extractCrateInfo, crateList)

def buildCreateItem(crate):
    return Item(
        id = 'python.rustdoc',
        text = crate['name'],
        subtext = f'{crate["name"]} - {crate["description"]}',
        icon = rustIcon,
        completion = f'rustdoc {crate["name"]}',
        actions = [
            UrlAction('Show on docs.rs', f'https://docs.rs/{crate["name"]}/{crate["version"]}/'),
            ClipAction('Copy as dependency', f'{crate["name"]} = {crate["version"]}'),
            UrlAction('Show on crates.io', f'https://crates.io/crates/{crate["name"]}/'),
        ]
    )

def fetchSearchIndex(crateName):
    cacheDir = f'{cacheLocation()}/rustdoc'
    cachePath = f'{cacheDir}/search-index-{crateName}.json'

    if os.path.exists(cachePath) and time.time() - os.path.getmtime(cachePath) < 86400:
        with open(cachePath, 'r') as indexCache:
            return json.loads(indexCache.read())

    cratePage = req.get(f'https://docs.rs/{crateName}/')
    indexUrl = re.compile('search-index.*?js').search(cratePage.text)
    if not indexUrl:
        return None
    indexUrl = indexUrl.group()
    indexJs = req.get(f'{cratePage.url}../{indexUrl}').text

    vm = py_mini_racer.MiniRacer()
    vm.eval("var initSearch = () => {};")
    vm.eval("var addSearchOptions = () => {};")
    vm.eval(indexJs)

    index = vm.eval("JSON.stringify(searchIndex)")
    result = {
        "index": index,
        "path": cratePage.url
    }

    if not os.path.exists(cacheDir):
        os.mkdir(cacheDir)
    with open(cachePath, 'w') as indexCache:
        indexCache.write(json.dumps(result))

    return result

def createResultItem(crateName, index, result):
    module = re.sub(
        '</?span>g',
        '',
        result['displayPath']
    )
    # icon = typeIcons[result['ty']]
    icon = rustIcon
    description = f'{module}{result["name"]}'
    if result['desc']:
        description += f' - {result["desc"]}'

    return Item(
        id = 'python.rustdoc',
        text = result['name'],
        subtext = description,
        completion = f'rustdoc {crateName} {result["name"]}',
        icon = icon,
        actions = [
            UrlAction('Show on docs.rs', f'{index["path"]}../{result["href"]}')
        ]
    )

def handleQuery(query):
    if query.isTriggered:
        args = query.string.split()

        if not args or len(args) == 0:
            return Item(
                id = 'python.rustdoc',
                text = 'RustDoc',
                subtext = 'Type a crate name or `std` to start search',
                icon = rustIcon,
                completion = query.rawString
            )

        if len(args) == 1:
            return list(map(buildCreateItem, searchCrate(args[0])))

        crateName = args[0]
        query = ' '.join(args[1:])

        index = fetchSearchIndex(crateName)

        vm = py_mini_racer.MiniRacer()
        with open(f'{path}/search.js', 'r') as searchJs:
            vm.eval(searchJs.read())
        results = vm.eval(f'initSearch({index["index"]})("{query}").others')

        return [createResultItem(crateName, index, result) for result in results]
