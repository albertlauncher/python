# -*- coding: utf-8 -*-

"""Evaluate simple python expressions.

Synopsis: <trigger> <python expression>"""

#  Copyright (c) 2022-2023 Manuel Schneider

from albert import *
from builtins import pow
from math import *
import os

md_iid = "0.5"
md_version = "1.2"
md_name = "Python Eval"
md_description = "Evaluate Python code"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/python_eval"
md_maintainers = "@manuelschneid3r"


class Plugin(QueryHandler):

    def id(self):
        return __name__

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
                result = str(eval(stripped))
            except Exception as ex:
                result = str(ex)

            query.add(Item(
                id="py_eval",
                text=str(result),
                subtext=type(result).__name__,
                completion=query.trigger + result,
                icon=[self.iconPath],
                actions = [
                    Action("copy", "Copy result to clipboard", lambda r=str(result): setClipboardText(r)),
                    Action("exec", "Execute python code", lambda r=str(result): exec(stripped)),
                ]
            ))
