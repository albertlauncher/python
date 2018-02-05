# -*- coding: utf-8 -*-
import subprocess
from albertv0 import *

#METADATA
__iid__ = "PythonInterface/v0.1"
__prettyname__ = "WindowSwitcher"
__version__ = "1.0"
__trigger__ = "!"
__author__ = "Ed Perez"
__dependencies__ = []

def initialize():
    pass

def handleQuery(query):
    if query.string:
        stripped = query.string.strip()
        results = []
        for win in window_search(stripped):
            results.append(Item(id=__prettyname__,
                                icon=window_icon(win['wm_class']),
                                text=win['wm_class'].split('.')[-1].replace('-',' '),
                                subtext=win['wm_name'],
                                actions=[ProcAction("Switch Window",
                                                    ["wmctrl", '-i', '-a',win['wid']])]))
        return results

def window_list():
    _list = []
    out = subprocess.check_output(['wmctrl', '-l', '-x'])
    for line in out.splitlines():
        args = line.split(None,4)
        wm_class = args[2].decode('utf-8')
        if window_filter(wm_class):
            _list.append({
                'wid':args[0].decode('utf-8'),
                'wm_class':wm_class,
                'wm_name':args[4].decode('utf-8') if len(args) > 4 else ''
            })
    return _list

def window_search(filter=''):
    _list = []
    for win in window_list():
        if filter in win['wm_name'] or filter in win['wm_class']:
            _list.append(win)
    return _list

def window_icon(filter=''):
    icon_name = filter.split('.')[0]

    if filter in 'sun-awt-X11-XFramePeer.jetbrains-pycharm':
        icon_name='pycharm'

    return iconLookup(icon_name)

def window_filter(filter=''):
    filters = ['xfce4-panel.Xfce4-panel',
                'xfce4-terminal.Xfce4-terminal',
                'xfdesktop.Xfdesktop',
                'conky-semi.conky-semi',
                'spectrumyzer.Spectrumyzer',
                'plank.Plank',
                'albert.albert',]
    if filter in filters:
        return False
    return True