# -*- coding: utf-8 -*-

"""Translate text using Google Translate.
Usage: tr <src lang> <dest lang> <text>
Example: tr en fr hello

Check available languages here:
https://cloud.google.com/translate/docs/languages"""

from albertv0 import *
import json
import urllib.request
import urllib.parse

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Google Translate"
__version__ = "1.0"
__trigger__ = "tr "
__author__ = "Manuel Schneider"
__dependencies__ = []

ua = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
urltmpl = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=%s&tl=%s&dt=t&q=%s"

iconPath = iconLookup('config-language')
if not iconPath:
    iconPath = ":python_module"


def handleQuery(query):
    if query.isTriggered:
        fields = query.string.split()
        item = Item(id=__prettyname__, icon=iconPath, completion=query.rawString)
        if len(fields) >= 3:
            src = fields[0]
            dst = fields[1]
            txt = " ".join(fields[2:])
            url = urltmpl % (src, dst, urllib.parse.quote_plus(txt))
            req = urllib.request.Request(url, headers={'User-Agent': ua})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                result = data[0][0][0]
                item.text = result
                item.subtext = "%s-%s translation of %s" % (src.upper(), dst.upper(), txt)
                item.addAction(ClipAction("Copy translation to clipboard", result))
                return item
        else:
            item.text = __prettyname__
            item.subtext = "Enter a query in the form of \"&lt;srclang&gt; &lt;dstlang&gt; &lt;text&gt;\""
            return item
