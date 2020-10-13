# -*- coding: utf-8 -*-

"""linguee extension

translate ger-eng with linguee

Synopsis: <trigger> <word>"""


from albertv0 import *
import requests
import bs4
import os


lang = "deutsch-englisch"

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Linguee-deutsch-englisch"
__version__ = "0.1"
__trigger__ = "lin "
__author__ = "Lucky Lukert, David Koch"
__dependencies__ = ["beautifulsoup4"]

iconPath = os.path.join(os.path.dirname(__file__), "linguee.png")

def getItem(message):
    return Item(
        id=__prettyname__,
        icon=iconPath,
        text=message,
        subtext="Linguee",
        completion=__trigger__,
        actions=[],
    )


def str_from_html(html):
    # extract a meaningful string from a translation_item
    # the item might be a nested structure, so this function is recursive
    if type(html) is bs4.element.NavigableString:
        return html.strip()
    elif type(html) is bs4.element.Tag:
        # we are only interested in placeholders (eg. "etw.")
        # and translation_items
        if not any(
            cls in html.attrs["class"]
            for cls in ["main_item", "translation_item", "placeholder"]
        ):
            return ""

        return " ".join([str_from_html(tr) for tr in html.children]).strip()


def get_suggestions(query):
    response = requests.get(
        "https://www.linguee.de/" + lang + "/search?",
        # change the ch-parameter to get more/less results
        params={"qe": query, "source": "auto", "cw": "820", "ch": "1000"},
    )
    parsed = bs4.BeautifulSoup(response.text, "html.parser")
    # get all suggestions
    items = parsed.find_all("div", attrs={"class": "autocompletion_item"})
    results = []
    for item in items:
        # main_item is the suggested word
        result = {
            "word": str_from_html(item.find("div", attrs={"class": "main_item"})),
            "translations": [],
        }
        # find all translation_items for this item
        for transl in item.find_all("div", attrs={"class": "translation_item"}):
            transl_str = str_from_html(transl)
            result["translations"].append(transl_str)
        results.append(result)

    # print(results)
    return results


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
