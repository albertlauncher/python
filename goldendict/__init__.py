# -*- coding: utf-8 -*-
# Copyright (c) 2017-2024 Manuel Schneider

import os
import shutil

from albert import *

md_iid = '2.3'
md_version = '1.4'
md_name = 'GoldenDict'
md_description = 'Quick access to GoldenDict'
md_license = 'MIT'
md_url = 'https://github.com/albertlauncher/python/tree/main/goldendict'
md_authors = '@manuelschneid3r'


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(
            self, self.id, self.name, self.description,
            defaultTrigger='gd '
        )

        commands = [
            '/var/lib/flatpak/exports/bin/org.goldendict.GoldenDict',  # flatpak
            '/var/lib/flatpak/exports/bin/io.github.xiaoyifang.goldendict_ng',  # flatpak ng
            'goldendict',  # native
            'goldendict-ng',  # native ng
        ]

        executables = [e for e in [shutil.which(c) for c in commands] if e]

        if not executables:
            raise RuntimeError(f'None of the GoldenDict distributions found.')

        self.executable = executables[0]
        self.iconUrls = [f'xdg:{os.path.basename(self.executable)}']

        if len(executables) > 1:
            warning(f"Multiple GoldenDict commands found: {', '.join(executables)}")
            warning(f"Using {self.executable}")

    def handleTriggerQuery(self, query: TriggerQuery):
        q = query.string.strip()
        query.add(
            StandardItem(
                id=md_name,
                text=md_name,
                subtext=f"Look up '{q}' in GoldenDict",
                iconUrls=self.iconUrls,
                actions=[Action(md_name, md_name, lambda e=self.executable: runDetachedProcess([e, q]))],
            )
        )
