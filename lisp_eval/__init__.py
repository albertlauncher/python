# -*- coding: utf-8 -*-
# Copyright (c) 2025 Hormet Yiltiz

from builtins import pow
from pathlib import Path
import subprocess

from albert import *

md_iid = '2.3'
md_version = "1.6"
md_name = "S-Exp Eval"
md_description = "Evaluate S-Expression via Fennel or Emacs"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/main/fennel_eval"
md_authors = "@manuelschneid3r"

class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        # search for a language supporting S-Exp: fennel, janet, elisp, clojure, racket
        # TODO: this should be a configurable option
        # Users should make available the executables in the system PATH
        lang_opts = {
            'janet': {
                'prog': 'janet',
                'args': ['-e', '(print {})'],
                'url': 'https://janet-lang.org/assets/janet-big.png'
            },
            'fennel': {
                'prog': 'fennel',
                'args': ['-e', '(print {})'],
                'url': 'https://janet-lang.org/assets/janet-big.png'
            },
            'elisp': {
                'prog': 'emacs',
                'args': ['--batch', '--eval', '(print {})'],
                'url': 'https://www.gnu.org/software/emacs/images/emacs.png'
            },
            'racket': {
                'prog': 'racket',
                'args': ['-e', '(print {})'],
                'url': 'https://racket-lang.org/img/racket-logo.svg'
            },
        }
        self.lang_opts = lang_opts

        test_sexp = '(+ 1 1)'
        detected_langs = []
        for lang, args in lang_opts.items():
            script = args['args'][-1].format(test_sexp)
            try:
                proc = subprocess.run([args['prog'], *args['args'][0:-1], script], input=script.encode(),
                                      stdout=subprocess.PIPE)
                result = proc.stdout.strip()
                if result:
                    detected_langs.append(lang)
            except FileNotFoundError as ex:
                # TODO: does Albert has a logger?
                continue


        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(
            self, self.id, self.name, self.description,
            synopsis='<Evaluate Lisp S-Expression>',
            defaultTrigger='() '
        )
        self.detected_langs = detected_langs
        self.call_external = lang_opts[detected_langs[0]]
        self.iconUrls = self.call_external['url']

    def handleTriggerQuery(self, query):
        act = lambda script: (
            lambda: runDetachedProcess([
                self.call_external['prog'],
                *self.call_external['args'][0:-1],
                self.call_external['args'][-1].format(script)]
            )
        )

        stripped = query.string.strip()
        if stripped:
            try:
                result = act(stripped)

            except Exception as ex:
                result = ex

            result_str = str(result)

            query.add(StandardItem(
                id=self.id,
                text=result_str,
                subtext=type(result).__name__,
                inputActionText=query.trigger + result_str,
                iconUrls=self.iconUrls,
                actions = [
                    Action("copy", "Copy result to clipboard", lambda r=result_str: setClipboardText(r)),
                    Action("exec", "Evaluate S-Expression", lambda r=result_str: act(r)),
                ]
            ))

# if __name__ == '__main__':
#     plugin = Plugin()
#     plugin.run()