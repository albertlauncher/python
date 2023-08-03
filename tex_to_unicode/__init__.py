# -*- coding: utf-8 -*-

#  Copyright (c) 2022 Manuel Schneider

import re
import unicodedata
from pathlib import Path
from pylatexenc.latex2text import LatexNodes2Text

from albert import *

md_iid = '2.0'
md_version = "1.2"
md_name = "TeX to Unicode"
md_description = "Convert TeX mathmode commands to unicode characters"
md_license = "GPL-3.0"
md_url = "https://github.com/albertlauncher/python/"
md_lib_dependencies = "pylatexenc"
md_maintainers = "@DenverCoder1"


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis='<tex input>',
                                     defaultTrigger='tex ')
        PluginInstance.__init__(self, extensions=[self])
        self.COMBINING_LONG_SOLIDUS_OVERLAY = "\u0338"
        self.iconUrls = [f"file:{Path(__file__).parent}/tex.png"]

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
        return StandardItem(
            id=md_id,
            text=text,
            subtext=subtext,
            iconUrls=self.iconUrls,
            actions=actions,
        )

    def handleTriggerQuery(self, query: TriggerQuery) -> None:
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
