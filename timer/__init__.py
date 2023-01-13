# -*- coding: utf-8 -*-

"""Set up timers.

Lists all timers when triggered. Additional arguments in the form of "[[hours:]minutes:]seconds
[name]" let you set triggers. Empty field resolve to 0, e.g. "96::" starts a 96 hours timer.
Fields exceeding the maximum amount of the time interval are automatically refactorized, e.g.
"9:120:3600" resolves to 12 hours.

Synopsis: <trigger> [[[hours]:][minutes]:]seconds [name]"""

#  Copyright (c) 2022 Manuel Schneider

from albert import *
from threading import Timer
from time import strftime, time, localtime
import dbus
import os
from datetime import timedelta
import subprocess

md_iid = "0.5"
md_version = "1.2"
#md_id = "overwrite"
md_name = "Timer"
md_description = "Do brief, imperative things"
md_license = "BSD-2"
md_url = "https://url.com/to/upstream/sources/and/maybe/issues"
md_maintainers = ["Manuel S.", "googol42", "uztnus"]
md_lib_dependencies = ["dbus"]

iconPath = os.path.dirname(__file__)+"/time.svg"
soundPath = os.path.dirname(__file__)+"/bing.wav"
timers = []

bus_name = "org.freedesktop.Notifications"
object_path = "/org/freedesktop/Notifications"
interface = bus_name

class AlbertTimer(Timer):

    def __init__(self, interval, name):

        def timeout():
            subprocess.Popen(["aplay", soundPath])
            global timers
            timers.remove(self)
            title = 'Timer "%s"' % self.name if self.name else 'Timer'
            text = "Timed out at %s" % strftime("%X", localtime(self.end))
            notify = dbus.Interface(dbus.SessionBus().get_object(bus_name, object_path), interface)
            notify.Notify(md_name, 0, iconPath, title, text, [], {"urgency":2}, 0)

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

class Plugin(QueryHandler):
    def id(self):
        return __name__

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return 'timer '

    def handleQuery(self, query):
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
                    icon=[iconPath]
                )

            seconds = 0
            fields.reverse()
            for i in range(len(fields)):
                seconds += int(fields[i] if fields[i] else 0)*(60**i)

            query.add(Item(
                id=self.name(),
                text=str(timedelta(seconds=seconds)),
                subtext='Set a timer with name "%s"' % name if name else 'Set a timer',
                icon=[iconPath],
                actions=[Action("set-timer", "Set timer", lambda sec=seconds: startTimer(sec, name))]
            ))
            return

        # List timers
        items = []
        for timer in timers:
            m, s = divmod(timer.interval, 60)
            h, m = divmod(m, 60)
            identifier = "%d:%02d:%02d" % (h, m, s)

            timer_name_with_quotes = '"%s"' % timer.name if timer.name else ''
            items.append(Item(
                id=self.name(),
                text='Delete timer <i>%s [%s]</i>' % (timer_name_with_quotes, identifier),
                subtext="Times out %s" % strftime("%X", localtime(timer.end)),
                icon=[iconPath],
                actions=[Action("delete-timer", "Delete timer", lambda timer=timer: deleteTimer(timer))]
            ))

        if items:
            query.add(items)

        # Display hint item
        query.add(Item(
            id=self.name(),
            text="Add timer",
            subtext="Enter a query in the form of '%s[[hours:]minutes:]seconds [name]'" % self.defaultTrigger(),
            icon=[iconPath]
        ))
