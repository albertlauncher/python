# -*- coding: utf-8 -*-

"""
Translator using py-googletrans
"""

from locale import getdefaultlocale
from pathlib import Path
from time import sleep

from albert import *
from googletrans import Translator, LANGUAGES

md_iid = '2.0'
md_version = "1.2"
md_name = "Google Translate"
md_description = "Translate sentences using googletrans"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/"
md_lib_dependencies = "googletrans==3.1.0a0"
md_maintainers = "@manuelschneid3r"


class Plugin(TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis="[[src] dest] text",
                                     defaultTrigger='tr ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/google_translate.png"]
        self.translator = Translator()
        self.lang = getdefaultlocale()[0][0:2]

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if stripped:
            for _ in range(50):
                sleep(0.01)
                if not query.isValid:
                    return

            src = None
            dest, text = self.lang, stripped
            splits = text.split(maxsplit=1)
            if 1 < len(splits) and splits[0] in LANGUAGES:
                dest, text = splits[0], splits[1]
                splits = text.split(maxsplit=1)
                if 1 < len(splits) and splits[0] in LANGUAGES:
                    src = dest
                    dest, text = splits[0], splits[1]

            if src:
                translation = self.translator.translate(text, src=src, dest=dest)
            else:
                translation = self.translator.translate(text, dest=dest)

            query.add(StandardItem(
                id=md_id,
                text=translation.text,
                subtext=f'From {LANGUAGES[translation.src]} to {LANGUAGES[translation.dest]}',
                iconUrls=self.iconUrls,
                actions=[Action("copy", "Copy result to clipboard",
                                lambda t=translation.text: setClipboardText(t))]
            ))
