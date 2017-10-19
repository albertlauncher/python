# -*- coding: utf-8 -*-

"""Evaluate simple python expressions.
Use it with care every keystroke triggers an evaluation."""

from albertv0 import *
from math import *
import os

__iid__ = "PythonInterface/v0.1" 
__prettyname__ = "Python Eval"
__version__ = "1.0"
__trigger__ = "py "
__author__ = "Manuel Schneider"
__dependencies__ = []


iconPath = os.path.dirname(__file__)+"/python.svg"


def handleQuery(query):
    if query.isTriggered:
        item = Item(completion=query.rawString, icon=iconPath)
        stripped = query.string.strip()

        if stripped == '':
            item.text = "Enter a python expression"
            item.subtext = "Math is in the namespace, if installed also Numpy as 'np'"
            return [item]
        else:
            try:
                result = eval(stripped)
            except Exception as ex:
                result = ex
            item.text = str(result)
            item.subtext = type(result).__name__
            item.addAction(ClipAction("Copy result to clipboard", str(result)))
            item.addAction(FuncAction("Execute", lambda: exec(str(result))))
        return [item]
