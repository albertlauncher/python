# -*- coding: utf-8 -*-

"""Find emojis by name.

Synopsis: <trigger> <emoji name>"""

import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
from pathlib import Path
from albert import *

md_iid = '1.0'
md_version = "1.2"
md_name = "Emoji Picker"
md_description = "Find emojis by name"
md_license = "GPL-3.0"
md_url = "https://github.com/albertlauncher/python/tree/master/emoji"
md_maintainers = "@tyilo"
md_bin_dependencies = ["convert"]


EXTENSION_DIR = Path(__file__).parent
ALIASES_PATH = EXTENSION_DIR / "aliases.json"
EMOJI_PATH = EXTENSION_DIR / "emoji-test.txt"
ICON_DIR = Path(cacheLocation()) / "emojis"


ICON_DIR.mkdir(exist_ok=True, parents=True)


def icon_path(emoji):
    return ICON_DIR / f"{emoji}.png"


def convert_to_png(emoji, output_path):
    subprocess.run(
        [
            "convert",
            "-pointsize",
            "64",
            "-background",
            "transparent",
            f"pango:{emoji}",
            output_path,
        ]
    )


def schedule_create_missing_icons(emojis):
    executor = ThreadPoolExecutor()
    for emoji in emojis:
        path = icon_path(emoji["emoji"])
        if not path.exists():
            executor.submit(convert_to_png, emoji["emoji"], path)

    return executor


class Plugin(TriggerQueryHandler):
    def id(self):
        return __name__

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return ": "

    def synopsis(self):
        return "<emoji name>"

    def initialize(self):
        line_re = re.compile(
            r"""
            ^
            (?P<codepoints> .*\S)
            \s*;\s*
            (?P<status> \S+)
            \s*\#\s*
            (?P<emoji> \S+)
            \s*
            (?P<version> E\d+.\d+)
            \s*
            (?P<name> [^:]+)
            (?: : \s* (?P<modifiers> .+))?
            \n
            $
            """,
            re.VERBOSE,
        )

        with ALIASES_PATH.open("r") as f:
            aliases = json.load(f)

        self.emojis = []
        with EMOJI_PATH.open("r") as f:
            for line in f:
                if m := line_re.match(line):
                    e = m.groupdict()
                    if e["status"] == "fully-qualified":
                        search_tokens = [e["name"]]
                        if e["modifiers"]:
                            search_tokens.append(e["modifiers"])
                        e["aliases"] = [a.lower() for a in aliases.get(e["name"], [])]
                        search_tokens += e["aliases"]
                        e["search_tokens"] = search_tokens
                        self.emojis.append(e)

        self.icon_executor = schedule_create_missing_icons(self.emojis)

    def finalize(self):
        self.icon_executor.shutdown(wait=True, cancel_futures=True)

    def matched_emojis(self, query_tokens):
        for emoji in self.emojis:
            for w in query_tokens:
                if w not in " ".join(emoji["search_tokens"]):
                    break

                yield emoji

    def handleTriggerQuery(self, query):
        query_tokens = query.string.strip().lower().split()
        if not query_tokens:
            return

        for emoji in islice(self.matched_emojis(query_tokens), 100):
            query.add(
                Item(
                    id=f"emoji_{emoji['emoji']}",
                    text=f"{emoji['emoji']} {emoji['name']}",
                    subtext=emoji["modifiers"] or "",
                    icon=[str(icon_path(emoji["emoji"]))],
                    actions=[
                        Action(
                            "copy",
                            "Copy to clipboard",
                            lambda r=emoji["emoji"]: setClipboardText(r),
                        ),
                    ],
                )
            )
