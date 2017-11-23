"""CopyQ Clipboard Management"""

import subprocess
from albertv0 import *
from shutil import which
import json

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
    if (str(read(i)).indexOf(match) !== -1) {
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
        if query.string:
            return runCopyQScript(copyq_script_getMatches % query.string)
        else:
            return runCopyQScript(copyq_script_getAll)


def runCopyQScript(script):
    items = []
    proc = subprocess.run(['copyq', '-'], input=script.encode(), stdout=subprocess.PIPE)
    json_arr = json.loads(proc.stdout.decode())
    for json_obj in json_arr:
        row = json_obj['row']
        text = json_obj['text']
        if not text:
            text = "< No text >"
        else:
            text = " ".join(filter(None, text.replace("\n", " ").split(" ")))
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
