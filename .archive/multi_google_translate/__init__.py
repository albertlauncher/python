# -*- coding: utf-8 -*-

"""Use Google Translate to translate your sentence into multiple languages.

Visit the following link to check available languages: \
https://cloud.google.com/translate/docs/languages. To add or remove languages use modifier key \
when trigger is activated or go to: '~/.config/albert/org.albert.extension.mtr/config.json' \
Add or remove elements based on the ISO-Codes that you found on the google documentation page.

Synopsis: <trigger> [query]"""

#  Copyright (c) 2022 Manuel Schneider

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from time import sleep

from albert import (ClipAction, Item, ProcAction, UrlAction, configLocation,
                      iconLookup)

__title__ = "MultiTranslate"
__version__ = "0.4.2"
__triggers__ = "mtr "
__authors__ = "David Britt"

iconPath = iconLookup('config-language')
if not iconPath:
    iconPath = ":python_module"

ua = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
urltmpl = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=%s&dt=t&q=%s"
urlbrowser = "https://translate.google.com/#auto/%s/%s"
configurationFileName = "language_config.json"
configuration_directory = os.path.join(configLocation(), __title__)
language_configuration_file = os.path.join(configuration_directory, configurationFileName)
languages = []

def initialize():
    if os.path.exists(language_configuration_file):
        with open(language_configuration_file) as json_config:
            languages.extend(json.load(json_config)["languages"])
    else:
        languages.extend(["en", "zh-CN", "hi", "es", "ru", "pt", "id", "bn", "ar", "ms", "ja", "fr", "de"])
        try:
            os.makedirs(configuration_directory, exist_ok=True)
            try:
                with open(language_configuration_file, "w") as output_file:
                    json.dump({"languages": languages}, output_file)
            except OSError:
                print("There was an error opening the file: %s" % language_configuration_file)
        except OSError:
            print("There was an error making the directory: %s" % configuration_directory)


def handleQuery(query):
    results = []
    if query.isTriggered:

        # avoid rate limiting
        sleep(0.2)
        if not query.isValid:
            return

        item = Item(
            id=__title__,
            icon=iconPath,
            text=__title__,
            actions=[ProcAction("Open the language configuration file.",
                                commandline=["xdg-open", language_configuration_file])]
        )
        if len(query.string) >= 2:
            for lang in languages:
                try:
                    url = urltmpl % (lang, urllib.parse.quote_plus(query.string))
                    req = urllib.request.Request(url, headers={'User-Agent': ua})
                    with urllib.request.urlopen(req) as response:
                        #print(type())
                        #try:
                        data = json.loads(response.read().decode())
                        #except TypeError as typerr:
                        #    print("Urgh this type.error. %s" % typerr)
                        translText = data[0][0][0]
                        sourceText = data[2]
                        if sourceText == lang:
                            continue
                        else:
                            results.append(
                                Item(
                                    id=__title__,
                                    icon=iconPath,
                                    text="%s" % (translText),
                                    subtext="%s" % lang.upper(),
                                    actions=[
                                        ClipAction("Copy translation to clipboard", translText),
                                        UrlAction("Open in your Browser", urlbrowser % (lang, query.string))
                                    ]
                                )
                            )
                except urllib.error.URLError as urlerr :
                    print("Check your internet connection: %s" % urlerr)
                    item.subtext = "Check your internet connection."
                    return item
        else:
            item.subtext = "Enter a query: 'mtr &lt;text&gt;'. Languages {%s}" % ", ".join(languages)
            return item
    return results
