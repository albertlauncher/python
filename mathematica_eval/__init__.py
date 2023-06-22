# -*- coding: utf-8 -*-

import subprocess
from tempfile import NamedTemporaryFile
from threading import Lock

from albert import (Action, Item, TriggerQuery, TriggerQueryHandler,
                    setClipboardText)

md_iid = "1.0"
md_version = "1.0"
md_name = "Mathematica Eval"
md_description = "Evaluate Mathemtica code"
md_license = "GPL-3.0"
md_url = "https://github.com/albertlauncher/python/tree/master/mathematica_eval"
md_maintainers = "@tyilo"
md_bin_dependencies = ["wolframscript"]


class Plugin(TriggerQueryHandler):
    def id(self) -> str:
        return md_id

    def name(self) -> str:
        return md_name

    def description(self) -> str:
        return md_description

    def defaultTrigger(self) -> str:
        return "mma "

    def synopsis(self) -> str:
        return "<Mathematica expression>"

    def handleTriggerQuery(self, query: TriggerQuery) -> None:
        stripped = query.string.strip()
        if not stripped:
            return

        with NamedTemporaryFile("w") as f:
            f.write(stripped)
            f.flush()
            process = subprocess.Popen(
                ["wolframscript", "-print", "-f", f.name],
                encoding="utf-8",
                stdout=subprocess.PIPE,
            )

            while True:
                if not query.isValid:
                    process.kill()
                    return

                try:
                    output, _ = process.communicate(timeout=0.1)
                    break
                except subprocess.TimeoutExpired:
                    pass

        result_str = output.strip()

        query.add(
            Item(
                id=md_id,
                text=result_str,
                completion=query.trigger + result_str,
                icon=["xdg:wolfram-mathematica"],
                actions=[
                    Action(
                        "copy",
                        "Copy result to clipboard",
                        lambda r=result_str: setClipboardText(r),
                    ),
                ],
            )
        )
