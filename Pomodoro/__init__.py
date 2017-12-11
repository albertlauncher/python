"""Pomodoro extension

https://en.wikipedia.org/wiki/Pomodoro_Technique"""

from albertv0 import *
from shutil import which
import subprocess
import threading
import re
import time
import os

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Pomodoro"
__version__ = "1.0"
__author__ = "Manuel Schneider"
__dependencies__ = [""]


class PomodoroTimer:

    def __init__(self):
        self.isBreak = True
        self.timer = None

    def timeout(self):
        if self.isBreak:
            duration = self.pomodoroDuration * 60
            self.timer = threading.Timer(duration, self.timeout)
            self.endTime = time.time() + duration
            debug("Pomodoro start (%s min)" % self.pomodoroDuration)
            playSound(1)
            self.timer.start()
        else:
            self.remainingTillLongBreak -= 1
            if self.remainingTillLongBreak == 0:
                self.remainingTillLongBreak = self.count
                duration = self.longBreakDuration * 60
                playSound(3)
                debug("Pomodoro long break (%s min)" % self.breakDuration)
            else:
                duration = self.breakDuration * 60
                playSound(2)
                debug("Pomodoro break (%s min)" % self.breakDuration)
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


iconPath = os.path.dirname(__file__)+"/pomodoro.svg"
soundPath = os.path.dirname(__file__)+"/bing.wav"
pomodoro = PomodoroTimer()


def playSound(num):
    for x in range(num):
        t = threading.Timer(0.5*x, lambda: subprocess.Popen(["aplay", soundPath]))
        t.start()


def handleQuery(query):
    tokens = query.string.split()
    if tokens and "pomodoro".startswith(tokens[0].lower()):

        global pomodoro
        pattern = re.compile(query.string, re.IGNORECASE)
        item = Item(
            id=__prettyname__,
            icon=iconPath,
            text=pattern.sub(lambda m: "<u>%s</u>" % m.group(0), "Pomodoro Timer"),
            completion=query.rawString
        )

        if len(tokens) == 1 and pomodoro.isActive():
            item.addAction(FuncAction("Stop", lambda p=pomodoro: p.stop()))
            if pomodoro.isBreak:
                whatsNext = "Pomodoro"
            else:
                whatsNext = "Long break" if pomodoro.remainingTillLongBreak == 1 else "Short break"
            item.subtext = "Stop pomodoro (Next: %s at %s)" % (whatsNext, time.strftime("%X",
                                                                                time.localtime(pomodoro.endTime)))
            return item

        p_duration = 25
        b_duration = 5
        lb_duration = 15
        count = 4

        item.subtext = "Invalid parameters. Use <i> pomodoro [duration [break duration [long break duration [count]]]]</i>"
        if len(tokens) > 1:
            if not tokens[1].isdigit():
                return item
            p_duration = int(tokens[1])

        if len(tokens) > 2:
            if not tokens[2].isdigit():
                return item
            b_duration = int(tokens[2])

        if len(tokens) > 3:
            if not tokens[3].isdigit():
                return item
            lb_duration = int(tokens[3])

        if len(tokens) > 4:
            if not tokens[4].isdigit():
                return item
            count = int(tokens[4])

        if len(tokens) > 5:
            return item

        item.subtext = "Start new pomodoro timer (%s min/Break %s min/Long break %s min/Count %s)" % (p_duration, b_duration, lb_duration, count)
        item.addAction(FuncAction("Start",
                                  lambda p=p_duration, b=b_duration, lb=lb_duration, c=count:
                                  pomodoro.start(p, b, lb, c)))

        return item
