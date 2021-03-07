# -*- coding: utf-8 -*-

"""List and manage GNOME Wayland windows

Synopsis: <filter>"""

import ast
import json
import subprocess
from collections import namedtuple
from typing import List
from albert import Item, ProcAction, iconLookup


__title__ = "Window Switcher for GNOME on Wayland"
__version__ = "0.4.1"
__authors__ = ["Tomáš Vlk"]
__exec_deps__ = ["gdbus"]

Window = namedtuple("Window", ["wm_id", "wm_class", "title", "workspace"])


def windows_list() -> List[Window]:
    output = (
        subprocess.check_output(
            [
                "gdbus",
                "call",
                "-e",
                "-d",
                "org.gnome.Shell",
                "-o",
                "/org/gnome/Shell",
                "-m",
                "org.gnome.Shell.Eval",
                "global.display.get_tab_list(0,null).map(w=>[w.get_id(),w.get_wm_class(),w.get_title(),w.get_workspace().index()])"  # noqa
                # "org.gnome.Shell.Eval","global.get_window_actors().map(w=>w.get_meta_window()).map(w=>[w.get_id(),w.get_wm_class(),w.get_title(),w.get_workspace().index()])" # noqa
            ]
        )
        .decode("utf-8")
        .strip()
        .replace("(true", "(True")
        .replace("(false", "(False")
    )
    value = ast.literal_eval(output)
    windows = json.loads(value[1]) if value[0] else []

    excluded_windows = ["Gnome-shell", "albert"]

    return [
        Window(wm_id, wm_class, title, workspace)
        for (wm_id, wm_class, title, workspace) in windows
        if wm_class not in excluded_windows
    ]


def window_icon(wm_class: str = ""):
    icon_name = wm_class.split(".")[-1].lower()

    if wm_class in "sun-awt-X11-XFramePeer.jetbrains-pycharm":
        icon_name = "pycharm"

    if wm_class in "sun-awt-X11-XFramePeer.jetbrains-phpstorm":
        icon_name = "phpstorm"

    if wm_class in "gnome-terminal-server.Gnome-terminal":
        icon_name = "terminal"

    if wm_class in "jetbrains-webstorm":
        icon_name = "webstorm"

    return iconLookup(icon_name)


def window_search(windows, query: str) -> List[Window]:
    if not query:
        return windows

    return [
        window
        for window in windows
        if query in window.wm_class.lower() or query in window.title.lower()
    ]


def handleQuery(query):

    query = query.string.strip().lower()
    windows = windows_list()
    filtered_windows = window_search(windows, query)

    return [
        Item(
            id=str(window.wm_id),
            icon=window_icon(window.wm_class),
            text="\u27f6<sup>%s</sup> <i>%s</i>"
            % (
                window.workspace,
                window.wm_class.split(".")[-1].replace("-", " ").capitalize(),
            ),
            subtext=window.title,
            actions=[
                ProcAction(
                    "Switch Window",
                    [
                        "gdbus",
                        "call",
                        "-e",
                        "-d",
                        "org.gnome.Shell",
                        "-o",
                        "/org/gnome/Shell",
                        "-m",
                        "org.gnome.Shell.Eval",
                        f"const Main=imports.ui.main; const window=global.get_window_actors().map(w=>w.get_meta_window()).filter(w=>w.get_id()=={window.wm_id})[0]; Main.activateWindow(window)",  # noqa
                    ],
                )
            ],
        )
        for window in filtered_windows
    ]
