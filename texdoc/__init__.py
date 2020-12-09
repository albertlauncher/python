# -*- coding: utf-8 -*-

"""texdoc extension

This is an extension to search for LaTeX documentation.

Synopsis: <trigger> <query>"""

import re
import subprocess

from shutil   import which
from pathlib  import Path
from albertv0 import *

__iid__          = 'PythonInterface/v0.3'
__prettyname__   = 'TeXdoc'
__version__      = '1.0'
__trigger__      = 'td'
__author__       = 'Florian Adamsky (@cit)'
__dependencies__ = ['texdoc']

iconPath   = Path(__file__).parent / 'texdoc-logo.svg'
texdoc_cmd = ['texdoc', '-I', '-q', '-s', '-M']

if which("texdoc") is None:
    raise Exception("'texdoc' is not in $PATH.")

def handleQuery(query):
    if not query.isTriggered:
        return

    query.disableSort()

    stripped_query = query.string.strip()

    if stripped_query:
        process = subprocess.run(texdoc_cmd + [stripped_query],
                              stdout=subprocess.PIPE)
        texdoc_output = process.stdout.decode('utf-8')

        results = []
        for line in texdoc_output.split("\n"):

            match = re.search('\t(/.*/)([\w\.-]+)\t\t', line, re.IGNORECASE)
            if match:
                directory = match.group(1).strip()
                filename  = match.group(2).strip()
                full_path = directory.join(['/', filename])

                results.append(Item(id         = __prettyname__,
                                    icon       = str(iconPath),
                                    text       = filename,
                                    subtext    = directory,
                                    completion = full_path,
                                    actions    = [
                                        ProcAction(text = 'This action opens the documentation.',
                                                   commandline=['xdg-open', full_path])
                                    ]))

        return results
    else:
        return Item(id         = __prettyname__,
                    icon       = str(iconPath),
                    text       = __prettyname__,
                    subtext    = 'Enter a query to search with texdoc',
                    completion = query.rawString)
