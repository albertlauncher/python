# -*- coding: utf-8 -*-

"""linguee extension

translate english-<lang> with linguee

Synopsis: <trigger> <lang> <word>

supported languages: de (German), es (Spanish), fr (French), it (Italian), ja (Japanese), nl (Dutch), pl (Polish), pt (Portuguese),ru (Russian), zh (Chinese)
"""


from albertv0 import *
import requests
from xml.etree import ElementTree
import os

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Linguee"
__version__ = "1.0"
__trigger__ = "lin "
__author__ = "Lucky Lukert, David Koch"
__dependencies__ = []

iconPath = os.path.join(os.path.dirname(__file__), "linguee.svg")

languages = {
    "de": "german",
    "es": "spanish",
    "fr": "french",
    "it": "italian",
    "ja": "japanese",
    "nl": "dutch",
    "pl": "polish",
    "pt": "portuguese",
    "ru": "russian",
    "zh": "chinese",
}

def getItem(message):
    return Item(
        id=__prettyname__,
        icon=iconPath,
        text=message,
        subtext="Linguee",
        completion=__trigger__,
        actions=[],
    )

def clean_translation_item(item):
    # the translation_item contains information like word type etc but we're
    # only interested in placeholders (like "sth.") so we remove everything else
    if len(item) == 0:
        return

    remove = []
    for i in item:
        if i.attrib["class"] != "placeholder":
            remove.append(i)
        else:
            clean_translation_item(i)  # the structure may be nested
    for r in remove:
        item.remove(r)



def get_results(linguee_response):
    linguee_response = linguee_response.replace("<span class='sep'>&middot;</span>","")
    linguee_response = linguee_response.replace("&","#-#")
    root = ElementTree.fromstring(linguee_response)
    results = []
    for item in root:
        word = item[0][0].text.strip()
        translations = []
        for translation_row in item[1:]:
            for translation_item in translation_row[0]:
                clean_translation_item(translation_item)
                translation = " ".join(tr.strip() for tr in translation_item.itertext()).strip()
                translations.append(translation)

        results.append({"word": word, "translations": translations})

    return results


def get_suggestions(lang, query):
    response = requests.get(
        "https://www.linguee.com/english-" + lang + "/search?",
        # change the ch-parameter to get more/less results
        params={"qe": query, "source": "auto", "cw": "820", "ch": "1000"},
    )
    return get_results(response.text)


def handleQuery(query):
    results = []
    if query.isTriggered:
        try:
            lang, query = query.string.split(maxsplit=1)
        except ValueError:
            # suggest supported languages
            suggestions = [
                Item(
                    icon=iconPath,
                    text=short,
                    subtext=long,
                    completion=__trigger__ + short,
                ) for short,long in languages.items()
            ]
            return [getItem("Please specify a language below")] + suggestions

        if lang not in languages:
            return [getItem("Language '{}' not supported".format(lang))]

        for result in get_suggestions(languages[lang], query):
            url = "http://www.linguee.com/english-{}/search?source=auto&query={}".format(
                languages[lang],
                result["word"]
            )
            results.append(
                Item(
                    id=result["word"],
                    icon=iconPath,
                    text=result["word"],
                    subtext=", ".join(result["translations"]),
                    completion=__trigger__ + result["word"],
                    actions=[
                        UrlAction("Open", url),
                        ClipAction("Copy url to clipboard", url)
                    ],
                )
            )
        if len(results) == 0:
            return [getItem("Sorry, there are no results.")]

    return results
