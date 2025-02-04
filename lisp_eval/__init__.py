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
from typing import List, Dict, Any, Optional
from pprint import pprint

from albert import *

md_iid = "2.4"
md_version = "2.4"
md_name = "S-Exp Eval"
md_description = "Evaluate S-Expression via Fennel, Emacs, Janet, Racket or Hylang."
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/main/lisp_eval/"
md_authors = "@hyiltiz"

_CONFIG_FILE = "config.json"


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        super().__init__()
        self.lang_opts: Dict[str, Any] = self._load_lang_options()
        self.detected_langs: List[str] = self._detect_languages()
        self._lang: Optional[str] = self._initialize_language()
        self._initialize_icon()
        self._initialize_trigger_query_handler()
        self._log_initialization()

    def _load_lang_options(self) -> Dict[str, Any]:
        """Load language options from the config file."""
        config_path = Path(__file__).parent / _CONFIG_FILE
        with config_path.open() as f:
            return json.load(f)

    def _detect_languages(self) -> List[str]:
        """Detect available languages that support S-Expressions.
        Users should make available the executables in the system PATH.
        """
        detected_langs: List[str] = []
        for lang, args in self.lang_opts.items():
            # R is secretly a Lisp too!
            test_sexp = "`+`(1, 1)" if lang.lower() == 'r' else "(+ 1 1)"
            script = args["args"][-1].format(test_sexp)
            debug(f"Testing {lang} with: {' '.join([args['prog'], *args['args'][0:-1], script])}")
            try:
                proc = subprocess.run(
                    [args["prog"], *args["args"][0:-1], script],
                    input=script.encode(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                result = proc.stdout.strip()
                if proc.returncode == 0 and result == b'2':
                    detected_langs.append(lang)
            except FileNotFoundError as ex:
                warning(f"Language {lang} not found: {ex}")
        return detected_langs

    def _initialize_language(self) -> str:
        """Initialize the language to be used for evaluation."""
        lang = self.readConfig("lang", str)
        if lang is None or lang not in self.detected_langs:
            lang = self.detected_langs[0]
            self.writeConfig("lang", lang)
        return lang

    def _initialize_icon(self):
        """Initialize the icon for the plugin."""
        icon_fname = Path(__file__).parent / self.lang_opts[self._lang]["url"]
        self.iconUrls = [f"file:{icon_fname}"] if icon_fname.exists() else [f"file:{Path(__file__).parent}/lambda.svg"]

    def _initialize_trigger_query_handler(self):
        """Initialize the trigger query handler."""
        TriggerQueryHandler.__init__(
            self,
            self.id,
            self.name,
            self.description,
            synopsis=f"<Evaluate S-Expression using {self.lang_opts[self._lang]['prog']}",
            defaultTrigger="() ",
        )

    def _log_initialization(self):
        """Log the initialization details."""
        debug(f"Completed plugin initialization for {self.name}")
        debug(f"Detected languages: {self.detected_langs}")
        debug(f"Using language: {self._lang}")
        info(f"{self.name} detected {self.detected_langs}. Using {self._lang}.")

    @property
    def lang(self) -> str:
        return self._lang

    @lang.setter
    def lang(self, value: str):
        self._lang = value
        self.writeConfig("lang", value)
        self._initialize_icon()

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
                "items": self.detected_langs,
            },
        ]

    def runSubprocess(self, query_script: str) -> str:
        """Run the subprocess to evaluate the S-Expression."""
        try:
            script = self.lang_opts[self._lang]["args"][-1].format(query_script)
            proc = subprocess.run(
                [self.lang_opts[self._lang]["prog"], *self.lang_opts[self._lang]["args"][0:-1], script],
                input=script.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            result = (
                proc.stderr.decode("utf-8", errors="replace").strip()
                + proc.stdout.decode("utf-8", errors="replace").strip()
            )
        except Exception as ex:
            critical(f"Python Subprocess call exception: {ex}")
            result = str(ex)
        return result

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if stripped:
            result = self.runSubprocess(stripped)
            query.add(
                StandardItem(
                    id=self.id,
                    text=result,
                    subtext=stripped,
                    inputActionText=f"{self.lang_opts[self._lang]['prog']}: {result}",
                    iconUrls=self.iconUrls,
                    actions=[
                        Action(
                            "copy",
                            "Copy result to clipboard",
                            lambda r=result: setClipboardText(r),
                        ),
                    ],
                )
            )