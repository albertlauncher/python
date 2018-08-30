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
import multiprocessing
import datetime
import tempfile
from functools import partial
from shutil import which

from albertv0 import *

import dbus


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


def parse_delay(query):
    delay = ''
    try:
        if query:
            delay = int(query.split()[-1])
            delay = '--delay=%s' % delay
    except ValueError:
        pass

    return delay


def command_notify(title, message):
    item = "org.freedesktop.Notifications"
    path = "/org/freedesktop/Notifications"
    interface = "org.freedesktop.Notifications"
    app_name = "Maim for Albert"
    id_num_to_replace = 0
    icon = ''
    actions_list = ''
    hint = ''
    time = 5000   # Use seconds x 1000

    bus = dbus.SessionBus()
    notif = bus.get_object(item, path)
    notify = dbus.Interface(notif, interface)
    notify.Notify(app_name, id_num_to_replace, icon,
                  title, message, actions_list, hint, time)

    return message


def command_screenshot(maim_args, _previous_result):
    filename = "%s-maim-screenshot.png" % datetime.datetime.now().isoformat()
    filename = os.path.join(get_screenshot_dir(), filename)

    cmd_sleep = 'sleep 1.0'
    cmd_maim = 'maim %s %s' % (maim_args, filename)
    cmd_copy = '{ echo "%s" | xclip -i -selection clipboard; }' % filename
    command = ' && '.join([cmd_sleep, cmd_maim, cmd_copy])
    subprocess.Popen(command, shell=True).wait()
    return filename


def command_open(url):
    subprocess.Popen('xdg-open %s' % url, shell=True).wait()
    return url


def command_imgur(filename):
    url = subprocess.check_output(
        'imgur %s ' % filename, shell=True).decode('utf8').splitlines()[0]
    cmd_copy = '{ echo -n "%s" | xclip -i -selection clipboard; }' % url
    subprocess.Popen(cmd_copy, shell=True).wait()
    return url


def handleQuery(query):
    if not query.isTriggered:
        return None

    stripped_query = query.string.strip()
    delay = parse_delay(stripped_query)

    command_screenshot_area_delay = partial(command_screenshot, "--select " + delay)
    command_screenshot_screen_delay = partial(command_screenshot, delay)
    command_notify_filename = partial(command_notify, 'Filename')
    command_notify_url = partial(command_notify, 'URL')

    return [
        Item(
            id="%s-area-of-screen-imgur" % __prettyname__,
            icon=iconPath,
            text="Area/Window, upload to Imgur [delay_seconds]",
            subtext="Draw a rectangle with your mouse to capture an area or pick a window",
            actions=[
                FuncAction(
                    "Take screenshot of selected area",
                    lambda: do_screenshot([
                        command_screenshot_area_delay,
                        command_imgur,
                        command_notify_url,
                        command_open,
                    ])
                ),
            ]
        ),
        Item(
            id="%s-area-of-screen" % __prettyname__,
            icon=iconPath,
            text="Area/Window [delay_seconds]",
            subtext="Draw a rectangle with your mouse to capture an area or pick a window",
            actions=[
                FuncAction(
                    "Take screenshot of selected area",
                    lambda: do_screenshot([
                        command_screenshot_area_delay,
                        command_notify_filename,
                        command_open,
                    ])
                ),
            ]
        ),
        Item(
            id="%s-whole-screen-imgur" % __prettyname__,
            icon=iconPath,
            text="Screen, upload to Imgur [delay_seconds]",
            subtext="Take a screenshot of the whole screen",
            actions=[
                FuncAction(
                    "Take screenshot of whole screen",
                    lambda: do_screenshot([
                        command_screenshot_screen_delay,
                        command_imgur,
                        command_notify_url,
                        command_open,
                    ])
                ),
            ]
        ),
        Item(
            id="%s-whole-screen" % __prettyname__,
            icon=iconPath,
            text="Screen [delay_seconds]",
            subtext="Take a screenshot of the whole screen",
            actions=[
                FuncAction(
                    "Take screenshot of whole screen",
                    lambda: do_screenshot([
                        command_screenshot_screen_delay,
                        command_notify_filename,
                        command_open,
                    ])
                ),
            ]
        ),
    ]


def get_screenshot_dir():
    if which("xdg-user-dir") is None:
        return tempfile.gettempdir()

    proc = subprocess.run(["xdg-user-dir", "PICTURES"], stdout=subprocess.PIPE)

    pictureDirectory = proc.stdout.decode("utf-8")
    if pictureDirectory:
        return os.path.expanduser(pictureDirectory.strip())

    return tempfile.gettempdir()


def run_in_process(commands, result):
    for command in commands:
        result = command(result)


def do_screenshot(commands):
    proc = multiprocessing.Process(target=run_in_process,
                                   args=(commands, None))
    proc.start()
    # we don't call wait() here to avoid blocking albert

