# -*- coding: utf-8 -*-

"""linguee extension

translate ger-eng with linguee

Synopsis: <trigger> <word>"""


from albertv0 import *
import requests
import bs4


lang = "deutsch-englisch"

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Linguee-deutsch-englisch"
__version__ = "0.1"
__trigger__ = "lin "
__author__ = "Lucky Lukert, David Koch"
__dependencies__ = ["beautifulsoup4"]

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
        params={"qe": query, "source": "auto", "cw": "820", "ch": "544"},
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

    return results


def handleQuery(query):
    results = []
    if query.isTriggered:
        for res in get_suggestions(query.string):
            results.append(
                Item(
                    id=res["word"],
                    icon=iconPath,
                    text=res["word"],
                    subtext=", ".join(res["translations"]),
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

    return results
