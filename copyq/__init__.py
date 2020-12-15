# -*- coding: utf-8 -*-

"""Access CopyQ clipboard.

Synopsis: <trigger> [filter]"""

import html
import json
import re
import subprocess

from albert import *

__title__ = "CopyQ"
__version__ = "0.4.1"
__triggers__ = "cq "
__authors__ = "manuelschneid3r"
__exec_deps__ = ["copyq"]


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
        query.disableSort()

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
                    id=__title__,
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
