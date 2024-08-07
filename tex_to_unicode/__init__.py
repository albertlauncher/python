# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Jonah Lawrence
#  Copyright (c) 2024 Manuel Schneider

import re
import unicodedata
from pathlib import Path
from pylatexenc.latex2text import LatexNodes2Text

from albert import *

md_iid = '2.3'
md_version = "1.3"
md_name = "TeX to Unicode"
md_description = "Convert TeX mathmode commands to unicode characters"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/tex_to_unicode"
md_authors = ["@DenverCoder1", "@manuelschneid3r"]
md_lib_dependencies = "pylatexenc"


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self, self.id, self.name, self.description, defaultTrigger='tex ')
        self.COMBINING_LONG_SOLIDUS_OVERLAY = "\u0338"
        self.iconUrls = [f"file:{Path(__file__).parent}/tex.svg"]

    def _create_item(self, text: str, subtext: str, can_copy: bool):
        actions = []
        if can_copy:
            actions.append(
                Action(
                    "copy",
                    "Copy result to clipboard",
                    lambda t=text: setClipboardText(t),
                )
            )
        return StandardItem(
            id=self.id,
            text=text,
            subtext=subtext,
            iconUrls=self.iconUrls,
            actions=actions,
        )

    def handleTriggerQuery(self, query):
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
