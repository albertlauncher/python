# -*- coding: utf-8 -*-

"""CopyQ clipboard management."""

import html
import json
import re
import subprocess
from shutil import which

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "CopyQ"
__version__ = "1.0"
__trigger__ = "cq "
__author__ = "Manuel Schneider"
__dependencies__ = ["copyq"]


if which("copyq") is None:
    raise Exception("'copyq' is not in $PATH.")

iconPath = iconLookup('copyq')

copyq_script_getAll = r"""
var result=[];
for ( var i = 0; i < size(); ++i ) {
    var obj = {};
    obj.row = i;
    obj.mimetypes = str(read("?", i)).split("\n");
    obj.mimetypes.pop();
    obj.text = str(read(i));
    result.push(obj);
}
JSON.stringify(result);
"""

copyq_script_getMatches = r"""
var result=[];
var match = "%s";
for ( var i = 0; i < size(); ++i ) {
    if (str(read(i)).search(new RegExp(match, "i")) !== -1) {
        var obj = {};
        obj.row = i;
        obj.mimetypes = str(read("?", i)).split("\n");
        obj.mimetypes.pop();
        obj.text = str(read(i));
        result.push(obj);
    }
}
JSON.stringify(result);
"""


def handleQuery(query):
    if query.isTriggered:
        try:
            pattern = re.compile(query.string, re.IGNORECASE)
            critical(query.string)
        except re.error:
            return [
                Item(
                    id=__prettyname__,
                    icon=iconPath,
                    text="<b>Invalid regex!</b>",
                    subtext="",
                    actions=[],
                )
            ]

        escaped_query = query.string.replace('\\', '\\\\').replace('"', '\\"')
        script = copyq_script_getMatches % escaped_query if query.string else copyq_script_getAll

        proc = subprocess.run(['copyq', '-'], input=script.encode(), stdout=subprocess.PIPE)
        json_arr = json.loads(proc.stdout.decode())

        if not json_arr:
            return [
                Item(
                    id=__prettyname__,
                    icon=iconPath,
                    text="<b>No results found.</b>",
                    subtext="",
                    actions=[],
                )
            ]

        items = []
        for json_obj in json_arr:
            row = json_obj['row']
            text = json_obj['text']
            if not text:
                text = "<i>No text</i>"
            else:
                U_BEGIN = "@U_BEGIN_XXXXX@"
                U_END = "@U_END_XXXXX@"
                raw_text = " ".join(filter(None, text.replace("\n", " ").split(" ")))
                underlined_text = pattern.sub(lambda m: U_BEGIN + m.group(0) + U_END, raw_text)
                text = html.escape(underlined_text).replace(U_BEGIN, "<u>").replace(U_END, "</u>")
            items.append(
                Item(
                    id=__prettyname__,
                    icon=iconPath,
                    text=text,
                    subtext="%s: %s" % (row, ", ".join(json_obj['mimetypes'])),
                    actions=[
                        ProcAction("Paste", ["copyq", "select(%s); sleep(60); paste();" % row]),
                        ProcAction("Copy", ["copyq", "select(%s);" % row]),
                        ProcAction("Remove", ["copyq", "remove(%s);" % row]),
                    ]
                )
            )
        return items
