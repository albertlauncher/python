"""
Inline DuckDuckGo web search using the 'duckduckgo-search' library.
"""

from albert import *
from pathlib import Path
from duckduckgo_search import DDGS
from itertools import islice
from time import sleep

md_iid = '2.0'
md_version = '1.0'
md_name = 'DuckDuckGo'
md_description = 'Inline DuckDuckGo web search'
md_url = 'https://github.com/albertlauncher/python/duckduckgo'
md_lib_dependencies = "duckduckgo-search"


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis="<query>",
                                     defaultTrigger='ddg ')
        PluginInstance.__init__(self, extensions=[self])
        self.ddg = DDGS()
        self.iconUrls = [f"file:{Path(__file__).parent}/duckduckgo.svg"]

    def handleTriggerQuery(self, query):

        stripped = query.string.strip()
        if stripped:

            # dont flood
            for number in range(25):
                sleep(0.01)
                if not query.isValid:
                    return

            for r in islice(self.ddg.text(stripped, safesearch='off'), 10):
                query.add(
                    StandardItem(
                        id=md_id,
                        text=r['title'],
                        subtext=r['body'],
                        iconUrls=self.iconUrls,
                        actions=[Action("open", "Open link", lambda u=r['href']: openUrl(u))]
                    )
                )
