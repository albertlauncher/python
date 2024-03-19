# -*- coding: utf-8 -*-

import subprocess
from tempfile import NamedTemporaryFile
from threading import Lock

from albert import *

md_iid = "2.0"
md_version = "1.1"
md_name = "Mathematica Eval"
md_description = "Evaluate Mathemtica code"
md_license = "GPL-3.0"
md_url = "https://github.com/albertlauncher/python/tree/master/mathematica_eval"
md_maintainers = "@tyilo"
md_bin_dependencies = ["wolframscript"]


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis='<Mathematica expression>',
                                     defaultTrigger='mma ')
        PluginInstance.__init__(self, extensions=[self])

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
            StandardItem(
                id=md_id,
                text=result_str,
                inputActionText=query.trigger + result_str,
                iconUrls=["xdg:wolfram-mathematica"],
                actions=[
                    Action(
                        "copy",
                        "Copy result to clipboard",
                        lambda r=result_str: setClipboardText(r),
                    ),
                ],
            )
        )
