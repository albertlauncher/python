"""Search in Zeal offline docs."""

from subprocess import run
from albert import *

md_iid = '1.0'
md_version = '1.1'
md_name = 'Zeal'
md_description = 'Search in Zeal docs'
md_url = 'https://github.com/albertlauncher/python/zeal'
md_bin_dependencies = ['zeal']


class Plugin(TriggerQueryHandler):
    iconUrl = "xdg:zeal"

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return 'z '

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        if stripped:
            query.add(
                Item(
                    id=md_name,
                    text=md_name,
                    subtext=f"Search '{stripped}' in Zeal",
                    icon=[Plugin.iconUrl],
                    actions=[Action("zeal", "Search in Zeal", lambda s=stripped: runDetachedProcess(['zeal', s]))]
                )
            )
