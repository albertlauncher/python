# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

"""
Provides an item 'Inhibit sleep' which can be used to temporarily disable system suspension.

This is a prototype using `systemd-inhibit`. A sophisticated implementation would probably use the systemd D-Bus \
interface documented [here](https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html).
"""

from albert import *
from subprocess import Popen, TimeoutExpired

md_iid = '2.3'
md_version = '1.1'
md_name = 'Inhibit sleep'
md_description = 'Inhibit system sleep mode.'
md_license = "MIT"
md_url = 'https://github.com/albertlauncher/python/inhibit_sleep'
md_authors = "@manuelschneid3r"
md_bin_dependencies = ['systemd-inhibit', "sleep"]


class Plugin(PluginInstance, GlobalQueryHandler):

    def __init__(self):
        PluginInstance.__init__(self)
        GlobalQueryHandler.__init__(
            self, self.id, self.name, self.description,
            defaultTrigger='is '
        )
        self.proc = None

    def finalize(self):
        if self.proc:
            self.toggle()

    def toggle(self):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=1)
            except TimeoutExpired:
                self.proc.kill()
            self.proc = None
        else:
            self.proc = Popen(["systemd-inhibit",
                               "--what=idle:sleep", "--who=Albert", "--why=User",
                               "sleep", "infinity"])
            info(str(self.proc))

    def configWidget(self):
        return [
            {
                'type': 'label',
                'text': __doc__.strip(),
                'widget_properties': {
                    'textFormat': 'Qt::MarkdownText'
                }
            }
        ]

    def handleGlobalQuery(self, query):
        stripped = query.string.strip().lower()
        if stripped in "inhibit sleep":
            return [
                RankItem(
                    StandardItem(
                        id=md_name,
                        text=md_name,
                        subtext=f"{'Enable' if self.proc else 'Disable'} sleep mode",
                        iconUrls=[f"gen:?text=💤"],
                        actions=[Action("inhibit", "Toggle", self.toggle)]
                    ),
                    len(stripped)/len(md_name))

            ]
        return []
