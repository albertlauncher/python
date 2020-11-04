# -*- coding: utf-8 -*-

"""Set up timers.

Lists all timers when triggered. Additional arguments in the form of "[[hours:]minutes:]seconds
[name]" let you set triggers. Empty field resolve to 0, e.g. "96::" starts a 96 hours timer.
Fields exceeding the maximum amount of the time interval are automatically refactorized, e.g.
"9:120:3600" resolves to 12 hours.

Synopsis: <trigger> [[[hours]:][minutes]:]seconds [name]"""

from albertv0 import *
from threading import Timer
from time import strftime, time, localtime
import os
import subprocess

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Timer"
__version__ = "1.1"
__trigger__ = "timer "
__author__ = "Manuel Schneider, Andreas Preikschat"
__dependencies__ = []

iconPath = os.path.dirname(__file__)+"/time.svg"
soundPath = os.path.dirname(__file__)+"/bing.wav"
timers = []


class AlbertTimer(Timer):

    def __init__(self, interval, name):

        def timeout():
            subprocess.Popen(["aplay", soundPath])
            global timers
            timers.remove(self)
            subtext="Timed out at %s" % strftime("%X", localtime(self.end))
            if self.name:
                subprocess.Popen(['notify-send', 'Timer "%s"' % self.name, '-t', '0', subtext])
            else:
                subprocess.Popen(['notify-send', 'Timer', '-t', '0', subtext])

        super().__init__(interval=interval, function=timeout)
        self.interval = interval
        self.name = name
        self.begin = int(time())
        self.end = self.begin + interval
        self.start()


def startTimer(interval, name):
    global timers
    timers.append(AlbertTimer(interval, name))


def deleteTimer(timer):
    global timers
    timers.remove(timer)
    timer.cancel()


def formatSeconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def handleQuery(query):
    if query.isTriggered:

        if query.string.strip():
            args = query.string.strip().split(maxsplit=1)
            fields = args[0].split(":")
            name = args[1] if 1 < len(args) else ''
            if not all(field.isdigit() or field == '' for field in fields):
                return Item(
                    id=__prettyname__,
                    text="Invalid input",
                    subtext="Enter a query in the form of '%s[[hours:]minutes:]seconds [name]'" % __trigger__,
                    icon=iconPath,
                    completion=query.rawString
                )

            seconds = 0
            fields.reverse()
            for i in range(len(fields)):
                seconds += int(fields[i] if fields[i] else 0)*(60**i)

            return Item(
                id=__prettyname__,
                text=formatSeconds(seconds),
                subtext='Set a timer with name "%s"' % name if name else 'Set a timer',
                icon=iconPath,
                completion=query.rawString,
                actions=[FuncAction("Set timer", lambda sec=seconds: startTimer(sec, name))]
            )

        else:
            # List timers
            items = []
            for timer in timers:

                m, s = divmod(timer.interval, 60)
                h, m = divmod(m, 60)
                identifier = "%d:%02d:%02d" % (h, m, s)

                timer_name_with_quotes = '"%s"' % timer.name if timer.name else ''
                items.append(Item(
                    id=__prettyname__,
                    text='Delete timer <i>%s [%s]</i>' % (timer_name_with_quotes, identifier),
                    subtext="Times out %s" % strftime("%X", localtime(timer.end)),
                    icon=iconPath,
                    completion=query.rawString,
                    actions=[FuncAction("Delete timer", lambda timer=timer: deleteTimer(timer))]
                ))
            if items:
                return items
            # Display hint item
            return Item(
                id=__prettyname__,
                text="Add timer",
                subtext="Enter a query in the form of '%s[[hours:]minutes:]seconds [name]'" % __trigger__,
                icon=iconPath,
                completion=query.rawString
            )

