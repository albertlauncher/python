# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

"""
Translates text using the python package translators. See https://pypi.org/project/translators/
"""

from locale import getdefaultlocale
from pathlib import Path
from time import sleep

from albert import *
import translators as ts

md_iid = '2.2'
md_version = "1.5"
md_name = "Translator"
md_description = "Translate sentences using 'translators' package"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/translators"
md_authors = "@manuelschneid3r"
md_lib_dependencies = "translators"


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis="[[from] to] text",
                                     defaultTrigger='tr ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/google_translate.png"]

        self._translator = self.readConfig('translator', str)
        if self._translator is None:
            self._translator = 'google'

        self._lang = self.readConfig('lang', str)
        if self._lang is None:
            self._lang = getdefaultlocale()[0][0:2]

        try:
            languages = ts.get_languages(self.translator)
            self.src_languages = set(languages.keys())
            self.dst_languages = set(languages[self.lang])
        except Exception as e:
            warning(str(e))

    @property
    def translator(self):
        return self._translator

    @translator.setter
    def translator(self, value):
        self._translator = value
        self.writeConfig('translator', value)
        languages = ts.get_languages(self.translator)
        self.src_languages = set(languages.keys())
        self.dst_languages = set(languages[self.lang])

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, value):
        self._lang = value
        self.writeConfig('lang', value)

    def configWidget(self):
        return [
            {
                'type': 'label',
                'text': __doc__.strip(),
            },
            {
                'type': 'combobox',
                'property': 'translator',
                'label': 'Translator',
                'items': ts.translators_pool
            },
            {
                'type': 'lineedit',
                'property': 'lang',
                'label': 'Default language',
            }
        ]

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if stripped:
            for _ in range(50):
                sleep(0.01)
                if not query.isValid:
                    return

            if len(splits := stripped.split(maxsplit=2)) == 3 \
                    and splits[0] in self.src_languages and splits[1] in self.dst_languages:
                src, dst, text = splits
            elif len(splits := stripped.split(maxsplit=1)) == 2 and splits[0] in self.src_languages:
                src, dst, text = 'auto', splits[0], splits[1]
            else:
                src, dst, text = 'auto', self.lang, stripped

            try:
                translation = ts.translate_text(query_text=text,
                                                translator=self.translator,
                                                from_language=src,
                                                to_language=dst,
                                                timeout=5)

                query.add(StandardItem(
                    id=md_id,
                    text=translation,
                    subtext=f"{src.upper()} > {dst.upper()}",
                    iconUrls=self.iconUrls,
                    actions=[
                        Action(
                            "paste", "Copy to clipboard and paste to front-most window",
                            lambda t=translation: setClipboardTextAndPaste(t)
                        ),
                        Action("copy", "Copy to clipboard",
                               lambda t=translation: setClipboardText(t))
                    ]
                ))

            except Exception as e:

                query.add(StandardItem(
                    id=md_id,
                    text="Error",
                    subtext=str(e),
                    iconUrls=self.iconUrls
                ))

                warning(str(e))