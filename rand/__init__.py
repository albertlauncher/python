# -*- coding: utf-8 -*-

"""Draws a random integer.

This extension provides the rand item, which can be used with :
    - 1 argument a : draws an integer between 1 and a (included)
    - 2 argumens a, b: draws an integer between a and b (included)
    - 3 arguments a, b, nb: draws nb integers between a and b (included)

Synopsis:
        rand [min] max [numbers]
"""

import os

import random

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Rand"
__version__ = "0.1"
__trigger__ = "rand "
__author__ = "Cyprien Ruffino"
__dependencies__ = []


usage_string = "Usage: [min] max [numbers]"


def createBlankItem(text):
    return Item(
                id=__prettyname__,
                icon="rand/rand.png",
                text=str(text),
                subtext="",
                actions=[])


def handleQuery(query):
    if query.isTriggered:

        tokens = query.string.split(" ")
        
        # No arguments
        if len(tokens) == 1 and tokens[0] == "":    
            return createBlankItem(usage_string)

        # At least one argument
        try:
            tokens = [int(token) for token in tokens]
        except ValueError:
            return createBlankItem(usage_string)

        if len(tokens) == 1:
            b = tokens[0]
            rand = random.randint(1, b)
            return createBlankItem(str(rand))
        
        elif len(tokens) == 2:
            a, b = tokens
            rand = random.randint(a, b)
            return createBlankItem(str(rand))
            
        elif len(tokens) == 3:
            a, b, nb = tokens
            items = []
            for i in range(nb):
                rand = random.randint(a, b)
                items.append(createBlankItem(rand))
            return items
        
        else: 
            return createBlankItem(usage_string)
