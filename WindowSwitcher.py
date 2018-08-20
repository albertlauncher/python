""" Window Switcher extension for EWMH/NetWM compatible X Window Manager """

import os
import subprocess
from albertv0 import *
from shutil import which

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'Window Switcher'
__version__ = '1.0'
__trigger__ = 'wm '
__author__ = 'Benedict Dudel'
__dependencies__ = ['wmctrl', 'xprop']

if which('wmctrl') is None:
    raise Exception("'wmctrl' is not in $PATH.")

if which('xprop') is None:
    raise Exception("'xprop' is not in $PATH.")

userDesktopIcon = iconLookup('user-desktop')

def handleQuery(query):
    if query.isTriggered:
        if query.string.strip().startswith('desktop'):
            return handleDesktops(query)

        return handleWindows(query)

def handleDesktops(query):
    results = []

    desktops = getDesktopList(query.string.strip()[8:])
    for desktop in desktops:
        results.append(
            Item(
                id=desktop['id'],
                icon=userDesktopIcon,
                text=desktop['name'],
                subtext='Switch to desktop',
                completion="%s desktop %s" % (__trigger__, desktop['name']),
                actions=[
                    ProcAction(
                        'Switch to Desktop',
                        ['wmctrl', '-s', desktop['id']]
                    ),
                ]
            )
        )

    return results

def handleWindows(query):
    results = []

    windows = getWindowList(query.string.strip())
    for window in windows:
        if window['title'] == 'Desktop':
            result = Item(
                id=window['id'],
                icon=userDesktopIcon,
                text=window['application'],
                subtext=window['title'],
                completion="%s%s" % (__trigger__, window['application']),
                actions=[
                    ProcAction(
                        'Switch to Desktop',
                        ['wmctrl', '-k', 'on']
                    ),
                ]
            )
        else:
            result = Item(
                id=window['id'],
                icon=iconLookup(window['application'].lower()),
                text=window['application'],
                subtext=window['title'],
                completion="%s%s" % (__trigger__, window['application']),
                actions=[
                    ProcAction(
                        'Switch to window',
                        ['wmctrl', '-i', '-a', window['id']]
                    ),
                    ProcAction(
                        'Close',
                        ['wmctrl', '-i', '-c', window['id']]
                    )
                ]
            )
        results.append(result)

    return results

def getWindowList(filterQuery):
    windows = []

    result = subprocess.run(['wmctrl', '-l'], stdout=subprocess.PIPE)
    for line in result.stdout.decode('utf-8').splitlines():
        windowDetails = line.split()
        if filterQuery and filterQuery not in windowDetails[3]:
            continue

        xprop = subprocess.Popen(
            ['xprop', '-id', windowDetails[0], 'WM_CLASS'],
            stdout=subprocess.PIPE
        )
        awk = subprocess.Popen(
            ['awk', '/WM_CLASS/{print $4}'],
            stdin=xprop.stdout, stdout=subprocess.PIPE
        )

        windows.append({
            'id': windowDetails[0],
            'title': ' '.join(windowDetails[3:]),
            'application': awk.communicate()[0].strip()[1:-1],
        })

    return windows

def getDesktopList(filterQuery):
    desktops = []

    wmctrl = subprocess.run(['wmctrl', '-d'], stdout=subprocess.PIPE)
    for line in wmctrl.stdout.decode('utf-8').splitlines():
        desktopDetails = line.split()

        name = 'Desktop %s' % desktopDetails[0]
        if len(desktopDetails) >= 10:
            name = " ".join(desktopDetails[9:])

        if name == 'N/A' or (filterQuery and filterQuery not in name):
            continue

        desktops.append({
            'id': desktopDetails[0],
            'name': name,
        })

    return desktops
