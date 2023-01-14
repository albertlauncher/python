# -*- coding: utf-8 -*-

"""This is a simple python template extension.

This extension should show the API in a comprehensible way. Use the module docstring to provide a \
description of the extension. The docstring should have three paragraphs: A brief description in \
the first line, an optional elaborate description of the plugin, and finally the synopsis of the \
extension.

Synopsis: <trigger> [delay|throw] <query>"""

#  Copyright (c) 2022-2023 Manuel Schneider

from albert import *
import os
from time import sleep

md_iid = "0.5"
md_version = "1.3"
md_name = "API Test"
md_description = "Test the python API 0.5"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/api_test"
md_maintainers = "@manuelschneid3r"


class Plugin(QueryHandler):
    def id(self):
        return "someid";

    def name(self):
        return "somename";

    def description(self):
        return "somedesc";

    def initialize(self):
        info("initialize")

    def finalize(self):
        info("finalize")

    def extensions(self):
        return [self.e]

    def handleQuery(self, query):
        # Note that when storing a reference to query, e.g. in a closure, you must not use
        # query.isValid. Apart from the query being invalid anyway it will crash the application.
        # The Python type holds a pointer to the C++ type used for isValid(). The C++ type will be
        # deleted when the query is finished. Therefore getting isValid will result in a SEGFAULT.

        if query.string.startswith("delay"):
            sleep(2)
            return Item(id=__title__,
                        text="Delayed test item",
                        subtext="Query string: %s" % query.string,
                        icons=os.path.dirname(__file__)+"/plugin.svg")

        if query.string.startswith("throw"):
            raise ValueError('EXPLICITLY REQUESTED TEST EXCEPTION!')

        info(query.string)
        info(query.trigger)
        info(str(query.isValid))

        critical(query.string)
        warning(query.string)
        debug(query.string)
        debug(query.string)

        results = []

        item = Item()

        item.icon = ['xdg:albert']
        item.text = 'Python item containing %s' % query.string
        item.subtext = 'Python description'
        item.completion = 'Completion test'
        info(item.icon)
        info(item.text)
        info(item.subtext)
        info(item.completion)
        results.append(item)

        item = Item(id=md_id,
                    text="This is the primary text",
                    subtext="This is the subtext, some kind of description",
                    completion='Hellooohooo!',
                    icon=[os.path.dirname(__file__)+"/plugin.svg"],
                    actions=[
                        Action(
                            id="clip",
                            text="setClipboardText (ClipAction)",
                            callable=lambda: setClipboardText(text=configLocation())
                        ),
                        Action(
                            id="url",
                            text="openUrl (UrlAction)",
                            callable=lambda: openUrl(url="https://www.google.de")
                        ),
                        Action(
                            id="run",
                            text="runDetachedProcess (ProcAction)",
                            callable=lambda: runDetachedProcess(
                                cmdln=["espeak", "hello"],
                                workdir="~"
                            )
                        ),
                        Action(
                            id="term",
                            text="runTerminal (TermAction)",
                            callable=lambda: runTerminal(
                                script="[ -e issue ] && cat issue | echo /etc/issue not found.",
                                workdir="/etc",
                                close_on_exit=False
                            )
                        ),
                        Action(
                            id="notify",
                            text="sendTrayNotification",
                            callable=lambda: sendTrayNotification(
                                title="Title",
                                msg="Message"
                            )
                        )
                    ])
        results.append(item)

        info(configLocation())
        info(cacheLocation())
        info(dataLocation())

        query.add(results)
