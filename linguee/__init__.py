# -*- coding: utf-8 -*-

"""linguee extension

translate ger-eng with linguee

Synopsis: <trigger> <word>"""


from albertv0 import *
import requests
from xml.etree import ElementTree
import os


lang = "deutsch-englisch"

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Linguee-deutsch-englisch"
__version__ = "0.2"
__trigger__ = "lin "
__author__ = "Lucky Lukert, David Koch"
__dependencies__ = []

iconPath = os.path.join(os.path.dirname(__file__), "linguee.svg")

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
        word = item[0][0].text.strip().encode().decode("utf-8")
        translations = []
        for translation_row in item[1:]:
            for translation_item in translation_row[0]:
                clean_translation_item(translation_item)
                translation = " ".join(tr.strip() for tr in translation_item.itertext()).strip()
                translations.append(translation)

        results.append({"word": word, "translations": translations})

    return results


def get_suggestions(query):
    response = requests.get(
        "https://www.linguee.de/" + lang + "/search?",
        # change the ch-parameter to get more/less results
        params={"qe": query, "source": "auto", "cw": "820", "ch": "1000"},
    )
    return get_results(response.text)


def handleQuery(query):
    results = []
    if query.isTriggered:
        for result in get_suggestions(query.string):
            url = "http://www.linguee.de/{}/search?source=auto&query={}".format(
                lang,
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
