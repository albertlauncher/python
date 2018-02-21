"""CopyQ Snippets Clipboard Management"""

import subprocess
from albertv0 import *
from shutil import which
import json

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Snippets"
__version__ = "1.0"
__trigger__ = "s "
__author__ = "Nicolás Flores"
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
    obj.title = str(read("application/x-copyq-item-notes", i));
    result.push(obj);
}
JSON.stringify(result);
"""

copyq_script_getMatches = r"""
var result=[];
var match = "%s";
for ( var i = 0; i < size(); ++i ) {
    if (str(read("application/x-copyq-item-notes", i)).search(new RegExp(match, "i")) !== -1 || str(read(i)).search(new RegExp(match, "i")) !== -1 ) {
        var obj = {};
        obj.row = i;
        obj.mimetypes = str(read("?", i)).split("\n");
        obj.mimetypes.pop();
	obj.text = str(read(i));
	obj.title = str(read("application/x-copyq-item-notes", i));
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
    proc = subprocess.run(['copyq', 'tab', 'snippets', '-'], input=script.encode(), stdout=subprocess.PIPE)
    json_arr = json.loads(proc.stdout.decode())
    for json_obj in json_arr:
        row = json_obj['row']
        text = json_obj['text']
        title = json_obj['title']
        if not text:
            text = "< No text >"
        else:
            text = " ".join(filter(None, text.replace("\n", " ").split(" ")))
        items.append(
            Item(
                id=__prettyname__,
                icon=iconPath,
                text=title,
                subtext="%s: %s" % (row, text),
                actions=[
                    ProcAction("Paste", ["copyq", 'tab', 'snippets' , "select(%s); sleep(60); paste();" % row]),
                    ProcAction("Copy", ["copyq", 'tab', 'snippets' "select(%s);" % row]),
                    ProcAction("Remove", ["copyq", 'tab', 'snippets' "remove(%s);" % row]),
                ]
            )
        )
    return items
