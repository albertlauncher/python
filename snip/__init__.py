# -*- coding: utf-8 -*-

"""Take screenshots or snips using Gnome screenshot utiliy directly from the launcher. \

Select if a simple snip ready to paste, a full screenshot showing (default) or not the pointer, or a screenshot of the window in use.

Auto saved screenshots are located in XDG_PICTURES_DIR (Pictures folder)"""

import os
import subprocess
import tempfile
from shutil import which

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Snip"
__version__ = "1.0"
__trigger__ = "ss "
__author__ = "Fabián Pérez"
__dependencies__ = ["gnome-screenshot"]


if which("gnome-screenshot") is None:
    raise Exception("'gnome-screenshot' not found - $PATH.")

iconPath = os.path.dirname(__file__)+"/icon.png"


def handleQuery(query):
    if query.isTriggered:
        return [
            Item(
                id = "%s-area-of-screen" % __prettyname__,
                icon = iconPath,
                text = "Snip screen",
                subtext = "Capture a rectacle drawed with your mouse",
                actions = [
                    FuncAction(
                        "Capture to the clipboard",
                        lambda: doScreenshot(["-a -c"])
                    ),
					FuncAction(
                        "Capture and save in Pictures",
                        lambda: doScreenshot(["-a"])
                    ),
                ]
            ),
			Item(
                id = "%s-whole-screen" % __prettyname__,
                icon = iconPath,
                text = "Take screenshot",
                subtext = "Save a screenshot in Pictures",
                actions = [
                    FuncAction(
                        "Take screenshot of whole screen",
                        lambda: doScreenshot(["-p"])
                    ),
					FuncAction(
                        "Take screenshot without showing the pointer",
                        lambda: doScreenshot([])
                    ),
					FuncAction(
                        "Take screenshot of actual window only",
                        lambda: doScreenshot(["-w --border-effect=shadow"])
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
    file = os.path.join(getScreenshotDirectory(), )

    command = "sleep 0.1 && gnome-screenshot %s " % file
    proc = subprocess.Popen(command + " ".join(additionalArguments), shell=True)
