"""Extension wich basically wraps the commandline utility scrot to make
screenshots from albert. The extension supports taking screenshots of the whole
screen, an specific area or the current active window.

When the screenshot was made you will hear a sound wich indicates that the
screenshot was taken successfully.

Screenshots will be saved in your home directory by default."""

from albertv0 import *
from shutil import which

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "scrot"
__version__ = "1.0"
__trigger__ = "scrot "
__author__ = "Benedict Dudel"
__dependencies__ = ["scrot", "xclip"]


if which("scrot") is None:
    raise Exception("'scrot' is not in $PATH.")

if which("xclip") is None:
    raise Exception("'xclip' is not in $PATH.")

iconPath = iconLookup("camera-photo")
fileName = "%Y-%m-%d-%T-screenshot.png"


def handleQuery(query):
    if query.isTriggered:
        return [
            Item(
                id = "%s-whole-screen" % __prettyname__,
                icon = iconPath,
                text = "Screen",
                subtext = "Take a screenshot of the whole screen",
                actions = [
                    ProcAction(
                        "Take screenshot of whole screen",
                        ["scrot", "--delay", "1", fileName, "--exec", "xclip -selection c -t image/png < $f"]
                    ),
                    ProcAction(
                        "Take screenshot of multiple displays",
                        ["scrot", "--multidisp", "--delay", "1", fileName, "--exec", "xclip -selection c -t image/png < $f"]
                    ),
                ]
            ),
            Item(
                id = "%s-area-of-screen" % __prettyname__,
                icon = iconPath,
                text = "Area",
                subtext = "Draw a rectangle with our mouse to capture an area",
                actions = [
                    ProcAction(
                        "Take screenshot of selected area",
                        ["scrot", "--select", fileName, "--exec", "xclip -selection c -t image/png < $f"]
                    ),
                ]
            ),
            Item(
                id = "%s-current-window" % __prettyname__,
                icon = iconPath,
                text = "Window",
                subtext = "Take a screenshot of the current active window",
                actions = [
                    ProcAction(
                        "Take screenshot of window with borders",
                        ["scrot", "--focused", "--border", "--delay", "1", fileName, "--exec", "xclip -selection c -t image/png < $f"]
                    ),
                    ProcAction(
                        "Take screenshot of window without borders",
                        ["scrot", "--focused", "--delay", "1", fileName, "--exec", "xclip -selection c -t image/png < $f"]
                    ),
                ]
            ),
        ]
