"""
Inline codespace launcher.
"""

from albert import *
import subprocess
from pathlib import Path
from typing import Any
from dataclasses import dataclass
import json
from typing import List
from difflib import SequenceMatcher
import arrow

md_iid = '2.0'
md_version = '1.0'
md_name = 'Codespaces'
md_description = 'Find, open, delete and SSH to your codespaces'
md_maintainers = "@lawrencegripper"
md_url = 'https://github.com/albertlauncher/python/tree/master/codespaces'
md_lib_dependencies = ['arrow']


@dataclass
class GitStatus:
    ahead: int
    behind: int
    hasUncommittedChanges: bool
    hasUnpushedChanges: bool
    ref: str

    @staticmethod
    def from_dict(obj: Any) -> 'GitStatus':
        _ahead = int(obj.get("ahead"))
        _behind = int(obj.get("behind"))
        _hasUncommittedChanges = bool(obj.get("hasUncommittedChanges"))
        _hasUnpushedChanges = bool(obj.get("hasUnpushedChanges"))
        _ref = str(obj.get("ref"))
        return GitStatus(_ahead, _behind, _hasUncommittedChanges, _hasUnpushedChanges, _ref)

@dataclass
class Codespace:
    gitStatus: GitStatus
    lastUsedAt: str
    name: str
    repository: str

    @staticmethod
    def from_dict(obj: Any) -> 'Codespace':
        _gitStatus = GitStatus.from_dict(obj.get("gitStatus"))
        _lastUsedAt = str(obj.get("lastUsedAt"))
        _name = str(obj.get("name"))
        _repository = str(obj.get("repository"))
        return Codespace(_gitStatus, _lastUsedAt, _name, _repository)


def get_codespaces() -> List[Codespace]:
    command: str = "gh codespace list --json name,gitStatus,lastUsedAt,repository"
    response = subprocess.run(command.split(' '), capture_output=True)
    codespaces: List[dict] = json.loads(response.stdout)

    codespace_list: List[Codespace] = []
    for c in codespaces:
        codespace_list.append(Codespace.from_dict(c))
    return codespace_list

class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis="<codespace name, branch or repo>",
                                     defaultTrigger='cs ',
                                     supportsFuzzyMatching=True)
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/codespace.svg"]

    def handleTriggerQuery(self, query):

        ranked_items: List[RankItem] = []
        stripped = query.string.strip()

        for c in get_codespaces():
            full_type = c.repository+c.gitStatus.ref+c.name
            has_uncommitted_changes = '💡' if c.gitStatus.hasUncommittedChanges else ' '
            last_used_at = arrow.get(c.lastUsedAt).humanize()
            score = SequenceMatcher(None, stripped.lower(), full_type.lower()).ratio()
            ranked_items.append(
                RankItem(
                    StandardItem(
                        id=md_id,
                        text=f'{c.repository} {c.gitStatus.ref} {has_uncommitted_changes}',
                        subtext=f'{c.name} {last_used_at}',
                        iconUrls=self.iconUrls,
                        actions=[
                            Action("open", "Open", lambda n=c.name: runDetachedProcess(['gh', 'codespace', 'code', '--codespace', n])),
                            Action("ssh", "SSH", lambda n=c.name: runTerminal(f'gh codespace ssh --codespace {n}')),
                            Action("delete", "Delete", lambda n=c.name: runTerminal(f'gh codespace delete --codespace {n}', close_on_exit=True)),
                        ]
                    ),
                    score
                )
            )
        ranked_items.sort(key=lambda x: x.score, reverse=True)
        for i in map(lambda x: x.item, ranked_items):
            query.add(i)