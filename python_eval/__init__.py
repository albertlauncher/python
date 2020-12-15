# -*- coding: utf-8 -*-

"""Evaluate simple python expressions.

Synopsis: <trigger> <python expression>"""

from albert import *
from math import *
from builtins import pow
try:
    import numpy as np
except ImportError:
    pass
import os

__title__ = "Python Eval"
__version__ = "0.4.0"
__triggers__ = "py "
__authors__ = "manuelschneid3r"


iconPath = os.path.dirname(__file__)+"/python.svg"


def handleQuery(query):
    if query.isTriggered:
        item = Item(id=__title__, icon=iconPath)
        stripped = query.string.strip()

        if stripped == '':
            item.text = "Enter a python expression"
            item.subtext = "Math is in the namespace and, if installed, also Numpy as 'np'"
            return item
        else:
            try:
                result = eval(stripped)
            except Exception as ex:
                result = ex
            item.text = str(result)
            item.subtext = type(result).__name__
            item.addAction(ClipAction("Copy result to clipboard", str(result)))
            item.addAction(FuncAction("Execute", lambda: exec(str(result))))
        return item
