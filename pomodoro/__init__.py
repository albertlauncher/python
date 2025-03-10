# -*- coding: utf-8 -*-
#  Copyright (c) 2024 Manuel Schneider

"""
Wiki: [Pomodoro_Technique](https://en.wikipedia.org/wiki/Pomodoro_Technique).
"""

import threading
import time
from pathlib import Path

from albert import *

md_iid = "3.0"
md_version = "2.0"
md_name = "Pomodoro"
md_description = "Set up a Pomodoro timer"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/pomodoro"
md_authors = "@manuelschneid3r"


class PomodoroTimer:

    def __init__(self):
        self.isBreak = True
        self.timer = None
        self.notification = None
        self.remainingTillLongBreak = 0
        self.endTime = 0
        self.pomodoroDuration = 0
        self.breakDuration = 0
        self.longBreakDuration = 0
        self.count = 0

    def timeout(self):
        if self.isBreak:
            duration = self.pomodoroDuration * 60
            self.timer = threading.Timer(duration, self.timeout)
            self.endTime = time.time() + duration
            self.notification = Notification("PomodoroTimer", "Let's go to work!")
            self.timer.start()
        else:
            self.remainingTillLongBreak -= 1
            if self.remainingTillLongBreak == 0:
                self.remainingTillLongBreak = self.count
                self.notification = Notification("PomodoroTimer", "Take a long break (%s min)" % self.longBreakDuration)
                duration = self.longBreakDuration * 60
            else:
                self.notification = Notification("PomodoroTimer", "Take a short break (%s min)" % self.breakDuration)
                duration = self.breakDuration * 60
            self.endTime = time.time() + duration
            self.timer = threading.Timer(duration, self.timeout)
            self.timer.start()
        self.isBreak = not self.isBreak

    def start(self, pomodoroDuration, breakDuration, longBreakDuration, count):
        self.stop()
        self.pomodoroDuration = pomodoroDuration
        self.breakDuration = breakDuration
        self.longBreakDuration = longBreakDuration
        self.count = count
        self.remainingTillLongBreak = count
        self.isBreak = True
        self.timeout()

    def stop(self):
        if self.isActive():
            self.timer.cancel()
            self.timer = None

    def isActive(self):
        return self.timer is not None


class Plugin(PluginInstance, TriggerQueryHandler):

    default_pomodoro_duration = 25
    default_break_duration = 5
    default_longbreak_duration = 15
    default_pomodoro_count = 4

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)
        self.pomodoro = PomodoroTimer()
        self.iconUrls = [f"file:{Path(__file__).parent}/pomodoro.svg"]

    def defaultTrigger(self):
        return 'pomo '

    def synopsis(self, query):
        return '[duration [break duration [long break duration [count]]]]'

    def configWidget(self):
        return [
            {
                'type': 'label',
                'text': __doc__.strip(),
                'widget_properties': {'textFormat': 'Qt::MarkdownText'}
            }
        ]

    def handleTriggerQuery(self, query):
        item = StandardItem(
            id=self.id(),
            iconUrls=self.iconUrls,
        )

        if self.pomodoro.isActive():
            item.text = "Stop Pomodoro"
            item.actions = [Action("stop", "Stop", lambda pomo=self.pomodoro: pomo.stop())]
            if self.pomodoro.isBreak:
                whatsNext = "Pomodoro"
            else:
                whatsNext = "Long break" if self.pomodoro.remainingTillLongBreak == 1 else "Short break"
            item.subtext = "%s at %s" % (whatsNext, time.strftime("%X", time.localtime(self.pomodoro.endTime)))
            query.add(item)

        else:
            tokens = query.string.split()
            if len(tokens) > 4 or not all([t.isdigit() for t in tokens]):
                item.text = "Invalid parameters"
                item.subtext = "Use %s" % self.synopsis
                query.add(item)
            else:
                p = int(tokens[0]) if len(tokens) > 0 else self.default_pomodoro_duration
                b = int(tokens[1]) if len(tokens) > 1 else self.default_break_duration
                lb = int(tokens[2]) if len(tokens) > 2 else self.default_longbreak_duration
                c = int(tokens[3]) if len(tokens) > 3 else self.default_pomodoro_count

                item.text = "Start Pomodoro"
                item.subtext = f"{p} min, break {b} min, long break {lb} min, count {c}"
                item.actions = [Action("start", "Start",
                                       lambda _p=p, _b=b, _lb=lb, _c=c: self.pomodoro.start(_p, _b, _lb, _c))]
                query.add(item)
