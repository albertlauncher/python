# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Manuel Schneider

"""
https://en.wikipedia.org/wiki/Pomodoro_Technique
"""

import subprocess
import threading
import time
from pathlib import Path

from albert import *

md_iid = '2.0'
md_version = "1.3"
md_name = "Pomodoro"
md_description = "Set up a Pomodoro timer"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/pomodoro"
md_maintainers = "@manuelschneid3r"


class PomodoroTimer:

    def __init__(self):
        self.isBreak = True
        self.timer = None

    def timeout(self):
        if self.isBreak:
            duration = self.pomodoroDuration * 60
            self.timer = threading.Timer(duration, self.timeout)
            self.endTime = time.time() + duration
            sendTrayNotification("PomodoroTimer", "Let's go to work!")
            self.timer.start()
        else:
            self.remainingTillLongBreak -= 1
            if self.remainingTillLongBreak == 0:
                self.remainingTillLongBreak = self.count
                sendTrayNotification("PomodoroTimer", "Take a long break (%s min)" % self.longBreakDuration)
                duration = self.longBreakDuration * 60
            else:
                sendTrayNotification("PomodoroTimer", "Take a short break (%s min)" % self.breakDuration)
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
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis='[duration [break duration [long break duration [count]]]]',
                                     defaultTrigger='pomo ')
        PluginInstance.__init__(self, extensions=[self])
        self.pomodoro = PomodoroTimer()
        self.iconUrls = [f"file:{Path(__file__).parent}/pomodoro.svg"]

    def handleTriggerQuery(self, query):
        item = StandardItem(
            id=md_id,
            iconUrls=self.iconUrls,
            text=md_name
        )

        if self.pomodoro.isActive():
            item.actions = [Action("stop", "Stop", lambda p=self.pomodoro: p.stop())]
            if self.pomodoro.isBreak:
                whatsNext = "Pomodoro"
            else:
                whatsNext = "Long break" if self.pomodoro.remainingTillLongBreak == 1 else "Short break"
            item.subtext = "Stop pomodoro (Next: %s at %s)" \
                           % (whatsNext, time.strftime("%X", time.localtime(self.pomodoro.endTime)))
            query.add(item)

        else:
            tokens = query.string.split()
            if len(tokens) > 4 or not all([t.isdigit() for t in tokens]):
                item.subtext = "Invalid parameters. Use %s" % self.synopsis()
                query.add(item)
            else:
                p = int(tokens[0]) if len(tokens) > 0 else self.default_pomodoro_duration
                b = int(tokens[1]) if len(tokens) > 1 else self.default_break_duration
                lb = int(tokens[2]) if len(tokens) > 2 else self.default_longbreak_duration
                c = int(tokens[3]) if len(tokens) > 3 else self.default_pomodoro_count
                item.subtext = "Start new pomodoro timer (%s min, break %s min, long break %s min, count %s)"\
                               % (p, b, lb, c)
                item.actions = [Action("start", "Start", lambda p=p, b=b, lb=lb, c=c: self.pomodoro.start(p, b, lb, c))]
                query.add(item)
