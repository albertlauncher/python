# -*- coding: utf-8 -*-
# Copyright (c) 2024 Lorenzo Morelli

"""
This plugin is a password generator.
- By default, generated passwords are 16 chars lenght.
- Type the number of chars you like to change it.
- Once password has been generated, press Enter to save it into clipboard.
"""

import secrets
import string
from albert import StandardItem, Action, setClipboardText, PluginInstance, TriggerQueryHandler


__title__ = "PWGen"

md_iid = '3.0'
md_version = "0.0"
md_name = "PW Gen"
md_description = "Create random strong password"
md_license = "GPL-3"
md_url = "https://github.com/LorenzoMorelli/pw-gen-albert-python-plugin"
md_authors = ["@LorenzoMorelli"]


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self)
        PluginInstance.__init__(self)
        self.iconUrls = [
            "xdg:pw-logo",
            # f"file:{pathlib.Path(__file__).parent}/pw.svg"
        ]

    def genPass(self, length: int):
        punctuation = "!@.,;?=+-_()*:&$"
        # prepare the alphabet
        alphabet = string.ascii_letters + string.digits + punctuation
        
        # if lenght less then 6 we cannot include all the possible chars combination for a strong password
        if length < 6:
            # build the password randombly then
            return ''.join(secrets.choice(alphabet) for i in range(length))
        # else, build the password strongly
        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(length))
            if (
                any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.islower() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in punctuation for c in password)
                and sum(c.isalpha() for c in password)
            ):
                return password

    def handleTriggerQuery(self, query):
        # default lenght
        length = 16
        # get password lenght
        try:
            length = int(query.string.strip())
        except:
            pass

        # build password
        pw = self.genPass(length)

        # show password
        query.add(
            StandardItem(
                id=__title__,
                iconUrls=self.iconUrls,
                text=pw,
                subtext="Password length: " + str(length) + ". Click to copy it!",
                actions=[
                    Action(
                        "pw-cp", "Copy password to clipboard",
                        lambda: setClipboardText(pw)
                    )
                ]
            )
        )
    def defaultTrigger(self):
        return 'pw '

    def synopsis(self, query):
        return "<password length>"

    def configWidget(self):
        return [
            {
                'type': 'label',
                'text': __doc__.strip(),
                'widget_properties': {
                    'textFormat': 'Qt::MarkdownText'
                }
            }
        ]
