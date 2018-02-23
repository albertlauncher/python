# -*- coding: utf-8 -*-

"""Set up timers.

Lists all timers when triggered. Additional arguments in the form of [[hours:]minutes:]seconds let
you set triggers."""

from albertv0 import *
from threading import Timer
from time import strftime, time, localtime
import os
import subprocess

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Timer"
__version__ = "1.0"
__trigger__ = "timer "
__author__ = "Manuel Schneider"
__dependencies__ = []

iconPath = os.path.dirname(__file__)+"/time.svg"
soundPath = os.path.dirname(__file__)+"/bing.wav"
timers = []


class AlbertTimer(Timer):

    def __init__(self, interval):

        def timeout():
            subprocess.Popen(["aplay", soundPath])
            global timers
            timers.remove(self)

        super().__init__(interval=interval, function=timeout)
        self.interval = interval
        self.begin = int(time())
        self.end = self.begin + interval
        self.start()


def startTimer(interval):
    global timers
    timers.append(AlbertTimer(interval))


def deleteTimer(timer):
    global timers
    timers.remove(timer)


def formatSeconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def handleQuery(query):
    if query.isTriggered:

        if query.string.strip():
            fields = query.string.strip().split(":")
            if not all(field.isdigit() for field in fields):
                return Item(
                    id=__prettyname__,
                    text=identifier,
                    subtext="bbla",
                    icon=iconPath,
                    completion=query.rawString
                )

            seconds = 0
            fields.reverse()
            for i in range(len(fields)):
                seconds += int(fields[i])*(60**i)

            return Item(
                id=__prettyname__,
                text=formatSeconds(seconds),
                subtext="Set a timer",
                icon=iconPath,
                completion=query.rawString,
                actions=[FuncAction("Set timer", lambda sec=seconds: startTimer(sec))]
            )

        else:
            # List timers
            items = []
            for timer in timers:

                m, s = divmod(timer.interval, 60)
                h, m = divmod(m, 60)
                identifier = "%d:%02d:%02d" % (h, m, s)

                items.append(Item(
                    id=__prettyname__,
                    text="Delete timer <i>[%s]</i>" % identifier,
                    subtext="Times out %s" % strftime("%X", localtime(timer.end)),
                    icon=iconPath,
                    completion=query.rawString,
                    actions=[FuncAction("Delete timer", lambda timer=timer: deleteTimer(timer))]
                ))

            return items
