# -*- coding: utf-8 -*-
# Copyright (c) 2017-2014 Manuel Schneider

from pathlib import Path

from albert import *

md_iid = "3.0"
md_version = "2.0"
md_name = "Python Eval"
md_description = "Evaluate Python code"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/main/python_eval"
md_authors = "@manuelschneid3r"


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)
        self.iconUrls = [f"file:{Path(__file__).parent}/python.svg"]

    def synopsis(self, query):
        return "<Python expression>"

    def defaultTrigger(self):
        return "py "

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if stripped:
            try:
                result = eval(stripped)
            except Exception as ex:
                result = ex

            result_str = str(result)

            query.add(StandardItem(
                id=self.id(),
                text=result_str,
                subtext=type(result).__name__,
                inputActionText=query.trigger + result_str,
                iconUrls=self.iconUrls,
                actions = [
                    Action("copy", "Copy result to clipboard", lambda r=result_str: setClipboardText(r)),
                    Action("exec", "Execute python code", lambda r=result_str: exec(stripped)),
                ]
            ))
