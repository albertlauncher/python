# -*- coding: utf-8 -*-

#  Copyright (c) 2022 Manuel Schneider

import os
import re
import unicodedata

from albert import *
from pylatexenc.latex2text import LatexNodes2Text

md_iid = '1.0'
md_version = "1.1"
md_name = "TeX to Unicode"
md_description = "Convert TeX mathmode commands to unicode characters"
md_license = "GPL-3.0"
md_url = "https://github.com/albertlauncher/python/"
md_lib_dependencies = "pylatexenc"
md_maintainers = "@DenverCoder1"


class Plugin(TriggerQueryHandler):
    def id(self) -> str:
        return md_id

    def name(self) -> str:
        return md_name

    def description(self) -> str:
        return md_description

    def defaultTrigger(self) -> str:
        return "tex "

    def synopsis(self) -> str:
        return "<tex input>"

    def initialize(self) -> None:
        self.COMBINING_LONG_SOLIDUS_OVERLAY = "\u0338"
        self.icon = [os.path.dirname(__file__) + "/tex.png"]

    def _create_item(self, text: str, subtext: str, can_copy: bool) -> Item:
        actions = []
        if can_copy:
            actions.append(
                Action(
                    "copy",
                    "Copy result to clipboard",
                    lambda t=text: setClipboardText(t),
                )
            )
        return Item(
            id=md_id,
            icon=self.icon,
            text=text,
            subtext=subtext,
            actions=actions,
        )

    def handleTriggerQuery(self, query: Query) -> None:
        stripped = query.string.strip()

        if not stripped:
            return

        if not stripped.startswith("\\"):
            stripped = "\\" + stripped

        # Remove double backslashes (newlines)
        stripped = stripped.replace("\\\\", " ")

        # pylatexenc doesn't support \not
        stripped = stripped.replace("\\not", "@NOT@")

        n = LatexNodes2Text()
        result = n.latex_to_text(stripped)

        if not result:
            query.add(self._create_item(stripped, "Type some TeX math", False))
            return

        # success
        result = unicodedata.normalize("NFC", result)
        result = re.sub(r"@NOT@\s*(\S)", "\\1" + self.COMBINING_LONG_SOLIDUS_OVERLAY, result)
        result = result.replace("@NOT@", "")
        result = unicodedata.normalize("NFC", result)
        query.add(self._create_item(result, "Result", True))
