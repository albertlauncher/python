"""
Extension which basically wraps the command line utility maim to make
screenshots from albert. The extension supports taking screenshots of the whole
screen, an specific area or the current active window.

Also supports upload to imgur:
https://github.com/tangphillip/Imgur-Uploader/blob/master/imgur

When the screenshot is made, notification message using dbus module will be
sent to indicate that the screenshot has been taken successfully or that an
error has occurred.

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
__dependencies__ = ["maim", "slop", "xclip"]


for dependency in __dependencies__:
    if which(dependency) is None:
        raise Exception("'%s' is not in $PATH." % dependency)

iconPath = iconLookup("camera-photo")


TIMEOUT_SECONDS = 10


class CommandException(Exception):
    pass


def parse_delay(query):
    delay = ''
    try:
        if query:
            delay = int(query.split()[-1])
            delay = '--delay=%s' % delay
    except ValueError:
        pass

    return delay


def expect(command):
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    try:
        proc.wait(TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as e:
        raise CommandException('Command "%s" timed out: %s' % (command, e))

    stdout = proc.stdout.read().decode('utf8')
    stderr = proc.stderr.read().decode('utf8')

    if proc.returncode != 0:
        message = '\n'.join([str(proc.returncode), stdout, stderr])
        raise CommandException(
            'Command "%s" terminated with non-zero exit code %s' % (
                command, message))

    return stdout


def get_screenshot_dir():
    if which("xdg-user-dir") is None:
        return tempfile.gettempdir()

    proc = subprocess.run(["xdg-user-dir", "PICTURES"], stdout=subprocess.PIPE)

    pictureDirectory = proc.stdout.decode("utf-8")
    if pictureDirectory:
        return os.path.expanduser(pictureDirectory.strip())

    return tempfile.gettempdir()


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


def command_copy(text):
    subprocess.Popen('echo -n "%s" | xclip -i -selection clipboard' % text,
                     shell=True).wait()
    return text


def command_screenshot(maim_args, _previous_result):
    filename = "%s-maim-screenshot.png" % datetime.datetime.now().isoformat()
    filename = os.path.join(get_screenshot_dir(), filename)

    expect('sleep 1.0 && maim %s %s' % (maim_args, filename))
    command_copy(filename)
    return filename


def command_open(url):
    subprocess.Popen('xdg-open %s' % url, shell=True).wait()
    return url


def command_imgur(filename):
    stdout = expect('imgur %s ' % filename)
    lines = stdout.splitlines()
    if len(lines) == 0:
        raise CommandException('Unexpected output from imgur: %s' % stdout)

    url = lines[0].strip()
    command_copy(url)
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


def run_in_process(commands, result):
    try:
        for command in commands:
            result = command(result)
    except CommandException as e:
        command_notify('Error', str(e))


def do_screenshot(commands):
    proc = multiprocessing.Process(target=run_in_process,
                                   args=(commands, None))
    proc.start()
    # we don't call wait() here to avoid blocking albert
