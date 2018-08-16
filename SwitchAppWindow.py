import re
import subprocess

from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Switch App Window"
__version__ = "1.0"
__trigger__ = "w "
__author__ = "Markus Geiger <mg@evolution515.net>"
__id__ = "window"
__dependencies__ = []

iconPath = iconLookup("go-next")

def handleQuery(query):
    stripped = query.string.strip()
    if not query.isTriggered and not stripped:
        return

    results = []
    process = subprocess.Popen(['wmctrl', '-l'], stdout=subprocess.PIPE, encoding='utf8')

    output, error = process.communicate()

    patt = re.compile(r'^(\w+)\s+(\d+)\s+([^\s]+)\s+(.+)$')
    window_re = re.compile(r'^(.+)\s+-\s+(.+)$')

    for line in output.split('\n'):
        match = patt.match(line)
        if not match:
            continue

        window_id = match.group(1)
        fulltitle = match.group(4)
        if not query.string.lower() in fulltitle.lower():
            continue

        titlematch = window_re.match(fulltitle)

        if titlematch:
            windowtitle = titlematch.group(1)
            program_title = titlematch.group(2)
        else:
            program_title = fulltitle
            windowtitle = fulltitle

        results.append(
            Item(
                id="%s_%s" % (__id__, window_id),
                icon=iconPath,
                text=program_title,
                subtext=windowtitle,
                completion=query.rawString,
                actions=[
                    ProcAction("Focus", ["wmctrl", "-ia", window_id]),
                    ProcAction("Close", ["wmctrl", "-ic", window_id])
                ]
            )
        )
    return results


