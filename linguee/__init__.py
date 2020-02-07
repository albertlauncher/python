# -*- coding: utf-8 -*-

"""linguee extension

translate ger-eng with linguee

Synopsis: <trigger> <word>"""


from albertv0 import *
import requests
import xml.etree.ElementTree as ET
import html
import urllib


lang = "deutsch-englisch"

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Linguee-deutsch-englisch"
__version__ = "1.0"
__trigger__ = "lin "
__author__ = "Lucky Lukert"
__dependencies__ = []

iconPath = iconLookup("albert")


def getItem(message):
    return Item(
        id=__prettyname__,
        icon=iconPath,
        text=message,
        subtext="Linguee",
        completion=__trigger__,
        actions=[],
    )


def isbadText(s):
    badText = ["akk", "adj", "präp", "pron", "n", "nt", "v", "m", "p", "f", "pl", "adv"]
    if s.lower() in badText:
        return True
    if s.startswith("p-") or "/" in s:
        return True
    return False


def getLinguee(query):
    response = requests.get(
        "http://www.linguee.de/" + lang + "/search?",
        params={"qe": query, "source": "auto"},
    ).text
    response = response.replace("<span class='sep'>&middot;</span>", "")
    response = response.replace("&", "#-#")

    root = ET.fromstring(response)
    result = []
    for suggestion in root:
        word = html.unescape(suggestion[0][0].text.strip().replace("#-##", "&#"))
        trans = []
        if len(suggestion) > 1 and len(suggestion[1]) > 0:
            for translation in suggestion[1][
                0
            ]:  # note that this yields only the first line of results
                current = ""
                for text in translation.itertext():
                    text = html.unescape(text.strip().replace("#-##", "&#"))
                    if isbadText(text):
                        continue
                    current += text + " "
                trans += [(current.strip())]
        result += [{"word": word, "trans": trans}]
    return result


def handleQuery(query):
    results = []
    if query.isTriggered:
        if len(query.string) > 2:

            for res in getLinguee(query.string):
                results.append(
                    Item(
                        id=res["word"],
                        icon=iconPath,
                        text=res["word"],
                        subtext=", ".join(res["trans"]),
                        completion=__trigger__ + res["word"],
                        actions=[
                            UrlAction(
                                "Open",
                                "http://www.linguee.de/"
                                + lang
                                + "/search?source=auto&query="
                                + res["word"],
                            )
                        ],
                    )
                )
            if len(results) == 0:
                return [getItem("Sorry, there are no results.")]
        else:
            return [getItem("Type at least 3 chars.")]

    return results
