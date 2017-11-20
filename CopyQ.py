""" CopyQ Clipboard Management """

import subprocess
from albertv0 import *
from shutil import which

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "CopyQ"
__version__ = "1.0"
__trigger__ = "cq "
__author__ = "BarbUk, Benedict Dudel"
__dependencies__ = ["copyq"]


if which("copyq") is None:
    raise Exception("'copyq' is not in $PATH.")

iconPath = iconLookup('copyq')


def handleQuery(query):
    if query.isTriggered:
        if not query.string or query.string == "":
            return getLastItems()

        item = searchItems(query.string)
        if not item == None:
            return item

    return [Item(
            id=__prettyname__,
            icon=iconPath,
            text=__prettyname__,
            subtext="No entry found for your search query.",
            completion="",
            actions=[]
    )]

def getLastItems():
    size = getStackSize()
    if size >= 14:
        size = 14

    items = []
    for rowCounter in range(0, size):
        item = getCopyItem(rowCounter)
        if item == None:
            continue

        items.append(item)

    return items

def searchItems(queryValue):
    item = searchItemByValue(queryValue)
    if not item == None:
        return [item]

    item = searchItemByItemNumber(queryValue.strip())
    if not item == None:
        return [item]

    return None

def searchItemByValue(queryValue):
    size = getStackSize()
    if size >= 50:
        size = 50

    for rowNumber in range(0, size):
        result = subprocess.run(
            ['copyq', 'read', 'text/plain', "%s" % rowNumber],
            stdout=subprocess.PIPE
        )

        if not result.stdout:
            continue

        text = getStrippedClipboardText(result.stdout)
        if queryValue not in text:
            continue

        return getCopyItem(rowNumber)

    return None;

def searchItemByItemNumber(queryValue):
    return getCopyItem(queryValue)

def getStackSize():
    result = subprocess.run(['copyq', 'size'], stdout=subprocess.PIPE)

    return int(result.stdout)

def getCopyItem(rowNumber):
    result = subprocess.run(
        ['copyq', 'read', 'text/plain', "%s" % rowNumber],
        stdout=subprocess.PIPE
    )

    if not result.stdout:
        return None

    return getAlbertItem(rowNumber, result.stdout, "")

def getAlbertItem(id, text, subtext):
    text = getStrippedClipboardText(text)
    if not text:
        return None

    return Item(
            id="%s" % id,
            icon=iconPath,
            text="%s" % text,
            subtext="%s: %s" % (id, text),
            completion="",
            actions=[
                ProcAction("Paste", ["copyq", "select(%s); sleep(60); paste();" % id]),
                ProcAction("Copy", ["copyq", "select(%s);" % id]),
                ProcAction("Remove", ["copyq", "remove(%s);" % id]),
            ]
    )

def getStrippedClipboardText(text):
    text = str(text, 'utf-8')
    lines = text.splitlines()
    text = ' '.join(line.strip() for line in lines if line)

    return text.strip()
