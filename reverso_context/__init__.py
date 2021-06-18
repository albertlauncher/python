# -*- coding: utf-8 -*-

"""Translates words between 15 languages.
Takes advantage of the Reverso Context translator API for Python.
Inspired by Manuel Schneider's Google Translate extension.
More infos about Reverso API for Python at https://pypi.org/project/Reverso-API/

Synopsis: <trigger> <src_lang> <dest_lang> <text>
Languages: ar(Arabic), de(German), en(English), es(Spanish), fr(French),
he(Hebrew), it(Italian), ja(Japanese), nl(Dutch), pl(Polish), po(Portuguese),
ro(Romanian), ru(Russian), tr(Turkish), zh(Chinese)"""

import reverso_api.context
from albert import *

__title__ = "Reverso Context"
__version__ = "0.0.3"
__triggers__ = "rev "
__authors__ = "adum"

iconPath = iconLookup('config-language') or ":python_module"

def top_n_translations(source_text, source_lang, target_lang):
    n = 3
    api = reverso_api.context.ReversoContextAPI(source_text, '', source_lang, target_lang)
    results = list(api.get_translations())
    try:
        top_n_results = [result[1] for result in results[:n]]
        output = ""
        for result in top_n_results:
            output += result + ', '
        output = output[:-2]
    except:
        output = None
    
    return output

def handleQuery(query):
    if query.isTriggered:
        fields = query.string.split()
        item = Item(id=__title__, icon=iconPath)
        if len(fields) >= 3:
            src = fields[0]
            dst = fields[1]
            txt = " ".join(fields[2:])
            result = top_n_translations(txt, src, dst)
            item.text = result
#           item.subtext = "%s-%s translation of %s" % (src.upper(), dst.upper(), txt)
            item.subtext = ""
            item.addAction(ClipAction("Copy translation to clipboard", result))
            return item
        else:
            item.text = __title__
            item.subtext = "Enter a query in the form of "\
                           + "\"&lt;srclang&gt; &lt;dstlang&gt; &lt;text&gt;\""
            return item
