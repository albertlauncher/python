"""
Extension which basically wraps the command line utility maim to make
screenshots from albert. The extension supports taking screenshots of the whole
screen, an specific area or the current active window.

Also supports upload to imgur:
https://github.com/tangphillip/Imgur-Uploader/blob/master/imgur

When the screenshot is made, notify-send message will be sent to indicate that
the screenshot has been taken successfully.

Screenshots will be saved in XDG_PICTURES_DIR or in the temp directory."""

import os
import subprocess
import datetime
import tempfile
from shutil import which

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "maim/slop screenshot utility"
__version__ = "1.0"
__trigger__ = "maim "
__author__ = "Yuri Bochkarev"
# imgur is optional
__dependencies__ = ["maim", "slop", "notify-send", "xclip"]


for dependency in __dependencies__:
    if which(dependency) is None:
        raise Exception("'%s' is not in $PATH." % dependency)

iconPath = iconLookup("camera-photo")


def _parseDelay(query):
    delay = []
    try:
        if query:
            delay = int(query.split()[-1])
            delay = ['--delay=%s' % delay]
    except ValueError:
        pass

    return delay



def handleQuery(query):
    if query.isTriggered:
        stripped_query = query.string.strip()
        delay = _parseDelay(stripped_query)
        enable_imgur = 'imgur' in stripped_query.split()

        return [
            Item(
                id="%s-area-of-screen" % __prettyname__,
                icon=iconPath,
                text="Area/Window [imgur] [delay_seconds]",
                subtext="Draw a rectangle with your mouse to capture an area or pick a window",
                actions=[
                    FuncAction(
                        "Take screenshot of selected area",
                        lambda: doScreenshot(["--select"] + delay, enable_imgur)
                    ),
                ]
            ),
            Item(
                id="%s-whole-screen" % __prettyname__,
                icon=iconPath,
                text="Screen: maim [imgur] [delay_seconds]",
                subtext="Take a screenshot of the whole screen",
                actions=[
                    FuncAction(
                        "Take screenshot of whole screen",
                        lambda: doScreenshot([] + delay, enable_imgur)
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
        return os.path.expanduser(pictureDirectory.strip())

    return tempfile.gettempdir()


def doScreenshot(additionalArguments, enable_imgur):
    filename = "%s-maim-screenshot.png" % datetime.datetime.now().isoformat()
    filename = os.path.join(getScreenshotDirectory(), filename)

    args = ' '.join(additionalArguments)
    cmd_sleep = 'sleep 1.0'
    cmd_maim = 'maim %s %s' % (args, filename)
    cmd_copy = '{ echo "%s" | xclip -i -selection clipboard; }' % filename
    cmd_notify = 'notify-send -t 5000 "Screenshot Filename" "%s"' % filename

    command = ' && '.join([cmd_sleep, cmd_maim, cmd_copy, cmd_notify])

    if enable_imgur:
        cmd_imgur = 'URL=$(imgur %s | head -1) ' % filename
        cmd_copy = '{ echo -n "$URL" | xclip -i -selection clipboard; }'
        cmd_notify = 'notify-send -t 5000 "Screenshot URL" "$URL"'
        command = ' && '.join([command, cmd_imgur, cmd_copy, cmd_notify])

    info('maim command: %s' % command)
    proc = subprocess.Popen(command, shell=True)
