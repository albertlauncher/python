from albert import Action, Item, TriggerQuery, TriggerQueryHandler, runDetachedProcess  # pylint: disable=import-error

md_iid = '2.0'
md_version = '1.3'
md_name = 'GoldenDict'
md_description = 'Searches in GoldenDict'
md_url = 'https://github.com/albertlauncher/python/'
md_maintainers = '@stevenxxiu'
md_bin_dependencies = ['goldendict']


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis='query',
                                     defaultTrigger='gd ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = ["xdg:goldendict"]

    def handleTriggerQuery(self, query: TriggerQuery) -> None:
        query_str = query.string.strip()
        if not query_str:
            return

        query.add(
            StandardItem(
                id=md_name,
                text=md_name,
                subtext=f'Look up {query_str} using <i>GoldenDict</i>',
                iconUrls=self.iconUrls,
                actions=[Action(md_name, md_name, lambda: runDetachedProcess(['goldendict', query_str]))],
            )
        )
