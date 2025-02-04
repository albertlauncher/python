# -*- coding: utf-8 -*-
# Copyright (c) 2025 Hormet Yiltiz

"""
Evaluates an S-Expression using an available Lisp language. Choose from the detected interpreters.
"""

from builtins import pow
from pathlib import Path
import subprocess

from albert import *

md_iid = "2.3"
md_version = "1.0"
md_name = "S-Exp Eval"
md_description = "Evaluate S-Expression via Fennel, Emacs, Janet, Racket or Hylang."
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/main/lisp_eval/"
md_authors = "@hyiltiz"


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        # search for a language supporting S-Exp: fennel, janet, elisp, clojure, racket
        # TODO: this should be a configurable option
        # Users should make available the executables in the system PATH
        lang_opts = {
            "elisp": {
                "prog": "emacs",
                "args": ["--batch", "--eval", "(print {})"],
                "url": "emacs-small.png",
            },
            "elisp": {
                "prog": "Emacs",
                "args": ["--batch", "--eval", "(print {})"],
                "url": "emacs-small.png",
            },
            "fennel": {
                "prog": "fennel",
                "args": ["-e", "(print {})"],
                "url": "fennel.svg",
            },
            "janet": {
                "prog": "janet",
                "args": ["-e", "(print {})"],
                "url": "janet.png",
            },
            "hylang": {
                "prog": "hy", # this is a pip3 dependency: `hy`
                "args": ["-c", "(print {})"],
                "url": "cuddles.png",
            },
            "racket": {
                "prog": "racket",
                "args": ["-e", "(print {})"],
                "url": "racket.svg",
            },
        }
        self.lang_opts = lang_opts

        test_sexp = "(+ 1 1)"
        detected_langs = []
        for lang, args in lang_opts.items():
            script = args["args"][-1].format(test_sexp)
            print(f"Testing {lang} with test script {script}")
            try:
                proc = subprocess.run(
                    [args["prog"], *args["args"][0:-1], script],
                    input=script.encode(),
                    stdout=subprocess.PIPE,
                )
                result = proc.stdout.strip()
                if result:
                    detected_langs.append(lang)
                    pass # break DONE: unless we provide alternatives in drop-down menu, do not bother detecting the rest
            except FileNotFoundError as ex:
                warning(str(ex))
                continue

        PluginInstance.__init__(self)
        self.detected_langs = detected_langs

        self._detected_langs = self.readConfig('detected_langs', list[str])
        if self._detected_langs is None:
            self._detected_langs = detected_langs

        self._lang = self.readConfig('lang', str)
        if self._lang is None:
            self._lang = detected_langs[0]

        self.call_external = self.lang_opts[self._lang]
        self.iconUrls = [f"file:{Path(__file__).parent}/{self.call_external['url']}"]
        TriggerQueryHandler.__init__(
            self,
            self.id,
            self.name,
            self.description,
            synopsis=f"<Evaluate S-Expression using {detected_langs[0]}",
            defaultTrigger="() ",
        )


    @property
    def detected_langs(self):
        return self._detected_langs

    @detected_langs.setter
    def detected_langs(self, value):
        self._detected_langs = value
        self.writeConfig('detected_langs', value)

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, value):
        self._lang = value
        print('Setting lang to', self.lang)
        print('Setting _lang to', self._lang)
        self.writeConfig('lang', value)
        self.call_external = self.lang_opts[self._lang]
        self.iconUrls = [f"file:{Path(__file__).parent}/{self.call_external['url']}"]

    def configWidget(self):
        return [
            {
                'type': 'label',
                'text': __doc__.strip(),
            },
            {
                'type': 'combobox',
                'property': 'lang',
                'label': 'Lisp Interpreter',
                'items': self._detected_langs,
            },
        ]

    def runSubprocess(self, query_script):
        try:
            script = self.call_external["args"][-1].format(query_script)
            proc = subprocess.run(
                [
                    self.call_external["prog"],
                    *self.call_external["args"][0:-1],
                    script,
                ],
                input=script.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                capture_output=False,
                check=False,
            )
            print(f'---------- :runSubprocess: ----------------------------------------------------')
            print(f'stderr: {proc.stderr}, returncode: {proc.returncode}, type: {type(proc.stderr)}')
            print(f'stdout: {proc.stdout}, type: {type(proc.stdout)}')
            print('\n\n')
            result = proc.stderr.decode('utf-8', errors='replace').strip() + proc.stdout.decode('utf-8', errors='replace').strip()
        except Exception as ex:
            print(f'Python Subprocess call exception: {str(ex)}')
            result = str(ex)
        return result

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if stripped:
            try:
                result = self.runSubprocess(stripped)
            except Exception as ex:
                result = ex

            result_str = result

            query.add(
                StandardItem(
                    id=self.id,
                    text=result_str,
                    subtext=stripped,
                    inputActionText=self.call_external["prog"] + ": " + result_str,
                    iconUrls=self.iconUrls,
                    actions=[
                        Action(
                            "copy",
                            "Copy result to clipboard",
                            lambda r=result_str: setClipboardText(r),
                        ),
                    ],
                )
            )