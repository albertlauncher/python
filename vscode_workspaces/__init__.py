"""
Inline codespace launcher.
"""

from albert import *
import subprocess
from pathlib import Path
from typing import List
from difflib import SequenceMatcher

md_iid = '2.0'
md_version = '1.0'
md_name = 'VSCode Workspaces'
md_description = 'list and open recent vscode workspaces'
md_maintainers = "@lawrencegripper"
md_url = 'https://github.com/albertlauncher/python/tree/master/vscode_workspaces'
md_lib_dependencies = []


def get_recent_workspaces() -> List[str]:
    command: str = '''grep -h -r -s --only-matching -e '"vscode[-remote]*:.*"' -e '"file:///.*"' ~/.config/Code*/User/workspaceStorage'''
    response = subprocess.run(command, executable="/bin/bash", capture_output=True, shell=True)
    entries = response.stdout.decode('utf-8').splitlines()
    entries = list(map(lambda x: x.replace('"', '', -1), entries))
    entries.reverse()
    return entries

def score(query: TriggerQuery, item: Item) -> float:
    return SequenceMatcher(None, item.text.lower(), query.string.lower()).ratio()


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis="<workspace name>",
                                     defaultTrigger='vscode ',
                                     supportsFuzzyMatching=True)
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/code.svg"]

    def handleTriggerQuery(self, query):
        items: List[Item] = []

        for workspace_uri in get_recent_workspaces():
            items.append(
                StandardItem(
                        id=md_id,
                        text=workspace_uri,
                        iconUrls=self.iconUrls,
                        actions=[
                            Action("open", "Open", lambda w=workspace_uri: runDetachedProcess(['code', '--folder-uri', w])),
                        ]
                )
            )
        items.sort(key=lambda t: score(query, t), reverse=True)
        for i in items:
            query.add(i)