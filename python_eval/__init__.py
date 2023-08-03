# -*- coding: utf-8 -*-

from builtins import pow
from math import *
from pathlib import Path

from albert import *

md_iid = '2.0'
md_version = "1.5"
md_name = "Python Eval"
md_description = "Evaluate Python code"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/python_eval"


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis='<Python expression>',
                                     defaultTrigger='py ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/python.svg"]

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if stripped:
            try:
                result = eval(stripped)
            except Exception as ex:
                result = ex

            result_str = str(result)

            query.add(StandardItem(
                id=md_id,
                text=result_str,
                subtext=type(result).__name__,
                inputActionText=query.trigger + result_str,
                iconUrls=self.iconUrls,
                actions = [
                    Action("copy", "Copy result to clipboard", lambda r=result_str: setClipboardText(r)),
                    Action("exec", "Execute python code", lambda r=result_str: exec(stripped)),
                ]
            ))
