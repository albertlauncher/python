# -*- coding: utf-8 -*-

"""Take screenshots of screens, areas or windows.

This extension wraps the command line utility scrot to make screenshots from albert. When the \
screenshot was made you will hear a sound which indicates that the screenshot was taken \
successfully.Screenshots will be saved in XDG_PICTURES_DIR or in the temp directory.

Synopsis: <trigger>"""

import os
import subprocess
import tempfile
from shutil import which

from albert import FuncAction, Item, iconLookup

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "SCReenshOT utility"
__version__ = "1.0"
__trigger__ = "scrot "
__author__ = "Benedict Dudel"
__dependencies__ = ["scrot", "xclip"]

for dep in __dependencies__:
    if not which(dep):
        raise Exception("'%s' is not in $PATH." % dep)

iconPath = iconLookup("camera-photo")


def handleQuery(query):
    if query.isTriggered:
        return [
            Item(
                id = "%s-whole-screen" % __prettyname__,
                icon = iconPath,
                text = "Screen",
                subtext = "Take a screenshot of the whole screen",
                actions = [
                    FuncAction(
                        "Take screenshot of whole screen",
                        lambda: doScreenshot([])
                    ),
                    FuncAction(
                        "Take screenshot of multiple displays",
                        lambda: doScreenshot(["--multidisp"])
                    ),
                ]
            ),
            Item(
                id = "%s-area-of-screen" % __prettyname__,
                icon = iconPath,
                text = "Area",
                subtext = "Draw a rectangle with your mouse to capture an area",
                actions = [
                    FuncAction(
                        "Take screenshot of selected area",
                        lambda: doScreenshot(["--select"])
                    ),
                ]
            ),
            Item(
                id = "%s-current-window" % __prettyname__,
                icon = iconPath,
                text = "Window",
                subtext = "Take a screenshot of the current active window",
                actions = [
                    FuncAction(
                        "Take screenshot of window with borders",
                        lambda: doScreenshot(["--focused", "--border"])
                    ),
                    FuncAction(
                        "Take screenshot of window without borders",
                        lambda: doScreenshot(["--focused"])
                    ),
                ]
            ),
        ]

def getScreenshotDirectory():
    if which("xdg-user-dir") is None:
        return tempfile.gettempdir()

    proc = subprocess.run(["xdg-user-dir", "PICTURES"], stdout=subprocess.PIPE)

    pictureDirectory = proc.stdout.decode("utf-8")
    if pictureDirectory:
        return pictureDirectory.strip()

    return tempfile.gettempdir()

def doScreenshot(additionalArguments):
    file = os.path.join(getScreenshotDirectory(), "%Y-%m-%d-%T-screenshot.png")

    command = "sleep 0.1 && scrot --exec 'xclip -selection c -t image/png < $f' %s " % file
    proc = subprocess.Popen(command + " ".join(additionalArguments), shell=True)
