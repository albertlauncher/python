# -*- coding: utf-8 -*-

"""
Takes arguments in the form of '`[[hrs:]mins:]secs [name]`'. Empty fields resolve to `0`. \
Fields exceeding the maximum amount of the time interval are automatically refactorized.

Examples:
- `5:` starts a 5 minutes timer
- `1:: ` starts a 1 hour timer
- `120:` starts a 2 hours timer
"""

from albert import *
from time import strftime, time, localtime
from datetime import timedelta
import threading
from sys import platform
import os
import subprocess

md_iid = '1.0'
md_version = "1.5"
md_name = "Timer"
md_description = "Set up timers"
md_license = "BSD-2"
md_url = "https://github.com/albertlauncher/python/tree/master/timer"
md_maintainers = ["@manuelschneid3r", "@googol42", "@uztnus"]

class Timer(threading.Timer):

    def __init__(self, interval, name, callback):
        super().__init__(interval=interval,
                         function=lambda: callback(self))
        self.name = name
        self.begin = int(time())
        self.end = self.begin + interval
        self.start()


class Plugin(TriggerQueryHandler):

    def initialize(self):
        self.icons = [os.path.dirname(__file__)+"/time.svg"]
        self.soundPath = os.path.dirname(__file__)+"/bing.wav"
        self.timers = []

    def finalize(self):
        for timer in self.timers:
            timer.cancel()
        self.timers.clear()

    def startTimer(self, interval, name):
        self.timers.append(Timer(interval, name, self.onTimerTimeout))

    def deleteTimer(self, timer):
        self.timers.remove(timer)
        timer.cancel()

    def onTimerTimeout(self, timer):
        title = 'Timer "%s"' % timer.name if timer.name else 'Timer'
        text = "Timed out at %s" % strftime("%X", localtime(timer.end))
        sendTrayNotification(title, text)

        if platform == "linux":
            subprocess.Popen(["aplay", self.soundPath])
        elif platform == "darwin":
            subprocess.Popen(["afplay", self.soundPath])

        self.deleteTimer(timer)

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return 'timer '

    def synopsis(self):
        return '[[hrs:]mins:]secs [name]'

    def handleTriggerQuery(self, query):
        if not query.isValid:
            return

        if query.string.strip():
            args = query.string.strip().split(maxsplit=1)
            fields = args[0].split(":")
            name = args[1] if 1 < len(args) else ''
            if not all(field.isdigit() or field == '' for field in fields):
                return Item(
                    id=self.name(),
                    text="Invalid input",
                    subtext="Enter a query in the form of '%s[[hours:]minutes:]seconds [name]'" % self.defaultTrigger(),
                    icon=self.icons
                )

            seconds = 0
            fields.reverse()
            for i in range(len(fields)):
                seconds += int(fields[i] if fields[i] else 0)*(60**i)

            query.add(Item(
                id=self.name(),
                text=str(timedelta(seconds=seconds)),
                subtext='Set a timer with name "%s"' % name if name else 'Set a timer',
                icon=self.icons,
                actions=[Action("set-timer", "Set timer", lambda sec=seconds: self.startTimer(sec, name))]
            ))
            return

        # List timers
        items = []
        for timer in self.timers:
            m, s = divmod(timer.interval, 60)
            h, m = divmod(m, 60)
            identifier = "%d:%02d:%02d" % (h, m, s)

            timer_name_with_quotes = '"%s"' % timer.name if timer.name else ''
            items.append(Item(
                id=self.name(),
                text='Delete timer %s [%s]' % (timer_name_with_quotes, identifier),
                subtext="Times out %s" % strftime("%X", localtime(timer.end)),
                icon=self.icons,
                actions=[Action("delete-timer", "Delete timer", lambda timer=timer: self.deleteTimer(timer))]
            ))

        if items:
            query.add(items)