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
__version__ = "1.1"
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

def copyq_get_matches(substring):
    script = copyq_script_getMatches % substring
    proc = subprocess.run(['copyq', '-'], input=script.encode(), stdout=subprocess.PIPE)
    return json.loads(proc.stdout.decode())


def copyq_get_all():
    proc = subprocess.run(['copyq', '-'], input=copyq_script_getAll.encode(), stdout=subprocess.PIPE)
    return json.loads(proc.stdout.decode())


def handleQuery(query):
    if query.isTriggered:

        items = []
        pattern = re.compile(query.string, re.IGNORECASE)
        json_arr = copyq_get_matches(query.string) if query.string else copyq_get_all()
        for json_obj in json_arr:
            row = json_obj['row']
            text = json_obj['text']
            if not text:
                text = "<i>No text</i>"
            else:
                text = html.escape(" ".join(filter(None, text.replace("\n", " ").split(" "))))
                if query.string:
                    text = pattern.sub(lambda m: "<u>%s</u>" % m.group(0), text)
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
