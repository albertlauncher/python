# -*- coding: utf-8 -*-
# TODO: replace name
# Copyright (c) 2024

"""
Allows for advanced calculations and easy conversion

Basic arithmitics
* 10*(4+5)^2 = 810
* 9 mod 5
* 140+15%
Functions
* sqrt(2;3) | log(4;3) | sin5
Conversion
* 30 gallon to l = 113,56236
* 1m**3 in l = 1000
* 5 degrees in rad

see all: https://help.gnome.org/users/gnome-calculator/stable/
Note: not everything works, for example 'rand' doesn't work
"""

from albert import *
import subprocess
from pathlib import Path

md_iid = '2.3'
md_version = '1.0'
md_name = 'gnome-calculator'
md_description = 'Powerfull gnome-calculator plugin'
md_license = 'MIT/agpl-3.0'
md_url = 'https://github.com/albertlauncher/python/tree/main/genome-calculator'
# TODO: replace name
md_authors = ""

def create_RankItem(self, text, subtext, clip_text):
    return RankItem(
        StandardItem(
            id=self.id,
            iconUrls=[self.icon_path],
            text=text,
            subtext=subtext,
            actions=[
                Action(
                    id="copy",
                    text="Copy result to clipboard",
                    callable=lambda: setClipboardText(text=clip_text),
                )
            ],
        ),
        1
    )

class Plugin(PluginInstance, GlobalQueryHandler):

    def __init__(self):
        PluginInstance.__init__(self)
        GlobalQueryHandler.__init__(
            self, self.id, self.name, self.description,
            defaultTrigger='='
        )
        self.icon_path = f"file:{Path(__file__).parent}/icons/GNOME_Calculator_icon_2021.svg"

    def handleGlobalQuery(self, query):
        rank_items = []
        s = query.string.strip()
        if not s:
            return rank_items
    
        if s.startswith('='):  # remove '=', probably uncessary as it seems the program already removes it
            s = s[1:]

        answer = subprocess.run(["gnome-calculator", "-s", s], capture_output=True) 
        if answer.returncode==0:
            answer_str = answer.stdout.decode('utf-8')
            modified_str = "= "+answer_str
            rank_items.append(
                create_RankItem(self, text=modified_str, subtext="", clip_text=answer_str)
            )
        elif query.trigger == "=": #show error only when user uses prefix
            error_str = answer.stderr.decode('utf-8')
            rank_items.append(
                create_RankItem(self, text=error_str, subtext="", clip_text=error_str)
            )

        return rank_items

    def configWidget(self):
        return [{ 'type': 'label', 'text': __doc__.strip() }]
    

