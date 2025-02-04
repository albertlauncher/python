# -*- coding: utf-8 -*-
# Copyright (c) 2025 Hormet Yiltiz

"""
Evaluates an S-Expression using an available Lisp language. Choose from the detected interpreters.

The plugin looks for executables defined in the config.json file for a list of languages in the *system PATH*. Please install your preferred language support, then make its executable available in system PATH. For example, using Bash in your terminal:

pip3 install hy  # install hylang interpreter using your preferred package manager
hy --version     # ensure it is installed
which -a hy      # to see where it is installed to
sudo ln -s $(which hy) /usr/local/bin/  # make it available in system PATH


Now quit and restart Albert. In Albert Settings, select hylang as your Lisp Interpreter.
"""

from pathlib import Path
import json
import subprocess
from pprint import pprint

from albert import *

md_iid = "2.4"
md_version = "2.4"
md_name = "S-Exp Eval"
md_description = "Evaluate S-Expression via Fennel, Emacs, Janet, Racket or Hylang."
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/main/lisp_eval/"
md_authors = "@hyiltiz"

_config_file = "config.json"


class Plugin(PluginInstance, TriggerQueryHandler):
    @property
    def detected_langs(self):
        return self._detected_langs

    @detected_langs.setter
    def detected_langs(self, value):
        self._detected_langs = value
        self.writeConfig("detected_langs", value)

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, value):
        self._lang = value
        debug("Setting config.lang and self._lang: ", self._lang)
        self.writeConfig("lang", value)
        self.call_external = self.lang_opts[self._lang]
        icon_fname = Path(__file__).parent / self.call_external["url"]
        if icon_fname.exists():
            self.iconUrls = [f"file:{icon_fname}"]
        else:
            self.iconUrls = [f"file:{Path(__file__).parent}" + "/lambda.svg"]

    def __init__(self):
        # search for a language supporting S-Exp: fennel, janet, elisp, clojure, racket
        # Users should make available the executables in the system PATH

        lang_opts = json.load((Path(__file__).parent / Path(_config_file)).open())
        debug("-----: lisp_eval init: ---------")
        debug(str(type(lang_opts)))
        self.lang_opts = lang_opts

        detected_langs = []
        for lang, args in lang_opts.items():
            if lang.lower() == 'r':
                # R is secretly a Lisp too!
                test_sexp = "`+`(1, 1)"
            else:
                test_sexp = "(+ 1 1)"
            script = args["args"][-1].format(test_sexp)
            debug(f"Testing {lang} with:")
            debug(' '.join([args["prog"], *args["args"][0:-1], script]))
            try:
                proc = subprocess.run(
                    [args["prog"], *args["args"][0:-1], script],
                    input=script.encode(),
                    stdout=subprocess.PIPE,
                    capture_output=False,
                    check=False,
                )
                debug(str(proc))
                result = proc.stdout.strip()

                if (proc.stderr is None
                        and result is not None
                        and result == b'2'
                        and proc.returncode == 0):
                    debug(f'Adding : {lang}')
                    detected_langs.append(lang)
            except FileNotFoundError as ex:
                warning(str(ex))
                continue

            debug('\n')

        PluginInstance.__init__(self)
        self.detected_langs = detected_langs

        self._detected_langs = self.readConfig("detected_langs", list[str])
        if self._detected_langs is None or self._detected_langs != detected_langs:
            self.detected_langs = detected_langs
            self.writeConfig("detected_langs", detected_langs)

        self._lang = self.readConfig("lang", str)
        debug(f'config.lang = {self._lang}')
        if self._lang is None:
            self.lang = detected_langs[0]

        self.call_external = self.lang_opts[self._lang]
        icon_fname = Path(__file__).parent / self.call_external["url"]
        if icon_fname.exists():
            self.iconUrls = [f"file:{icon_fname}"]
        else:
            self.iconUrls = [f"file:{Path(__file__).parent}" + "/lambda.svg"]
        TriggerQueryHandler.__init__(
            self,
            self.id,
            self.name,
            self.description,
            synopsis=f"<Evaluate S-Expression using {self.call_external['prog']}",
            defaultTrigger="() ",
        )
        debug(f'Completed plugin initialization for {self.name}')
        debug(f'detected_langs: {detected_langs}')
        debug(f'self.detected_langs: {self.detected_langs}')
        debug(f'self._detected_langs: {self._detected_langs}')
        debug(f'config.detected_langs: {self.readConfig("detected_langs", list[str])}')
        info(f'{self.name} detected {self.detected_langs}. Using {self.lang}.')

    def configWidget(self):
        return [
            {
                "type": "label",
                "text": __doc__.strip(),
            },
            {
                "type": "combobox",
                "property": "lang",
                "label": "Lisp Interpreter",
                "items": self._detected_langs,
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
            debug(f"---------- :runSubprocess: ----------------------------------------------------")
            debug(str(proc))
            debug("\n\n")
            result = (
                proc.stderr.decode("utf-8", errors="replace").strip()
                + proc.stdout.decode("utf-8", errors="replace").strip()
            )
        except Exception as ex:
            critical(f"Python Subprocess call exception: {str(ex)}")
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
