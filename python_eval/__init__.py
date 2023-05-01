# -*- coding: utf-8 -*-
#  Copyright (c) 2022-2023 Manuel Schneider

from albert import *
from builtins import pow
from math import *
import os

md_iid = "0.5"
md_version = "1.3"
md_name = "Python Eval"
md_description = "Evaluate Python code"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/python_eval"
md_maintainers = "@manuelschneid3r"


class Plugin(QueryHandler):

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "py "

    def synopsis(self):
        return "<Python expression>"

    def initialize(self):
        self.iconPath = os.path.dirname(__file__)+"/python.svg"

    def handleQuery(self, query):
        stripped = query.string.strip()
        if stripped:
            try:
                result = eval(stripped)
            except Exception as ex:
                result = ex

            result_str = str(result)

            query.add(Item(
                id=md_id,
                text=result_str,
                subtext=type(result).__name__,
                completion=query.trigger + result_str,
                icon=[self.iconPath],
                actions = [
                    Action("copy", "Copy result to clipboard", lambda r=result_str: setClipboardText(r)),
                    Action("exec", "Execute python code", lambda r=result_str: exec(stripped)),
                ]
            ))
