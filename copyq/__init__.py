# -*- coding: utf-8 -*-
# Copyright (c) 2017-2024 Manuel Schneider
# Copyright (c) 2023 Oskar Haarklou Veileborg (@BarrensZeppelin)

import json
import subprocess

from albert import *

md_iid = "3.0"
md_version = "2.0"
md_name = "CopyQ"
md_description = "Access CopyQ clipboard"
md_license = "BSD-2-Clause"
md_url = "https://github.com/albertlauncher/python/tree/main/copyq"
md_authors = ["@ManuelSchneid3r", "@BarrensZeppelin"]
md_bin_dependencies = ["copyq"]


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


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

    def defaultTrigger(self):
        return "cp "

    def handleTriggerQuery(self, query):
        items = []
        script = copyq_script_getMatches % query.string if query.string else copyq_script_getAll
        proc = subprocess.run(["copyq", "-"], input=script.encode(), stdout=subprocess.PIPE)
        json_arr = json.loads(proc.stdout.decode())

        for json_obj in json_arr:
            row = json_obj["row"]
            text = json_obj["text"]
            if not text:
                text = "No text"
            else:
                text = " ".join(filter(None, text.replace("\n", " ").split(" ")))

            act = lambda s=script, r=row: (
                lambda: runDetachedProcess(["copyq", s % r])
            )
            items.append(
                StandardItem(
                    id=self.id(),
                    iconUrls=["xdg:copyq"],
                    text=text,
                    subtext="%s: %s" % (row, ", ".join(json_obj["mimetypes"])),
                    actions=[
                        Action("paste", "Paste", act("select(%s); sleep(60); paste();")),
                        Action("copy", "Copy", act("select(%s);")),
                        Action("remove", "Remove", act("remove(%s);")),
                    ],
                )
            )

        query.add(items)
