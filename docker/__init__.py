# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

import docker
from albert import *

md_iid = "2.0"
md_version = "1.6"
md_name = "Docker"
md_description = "Manage docker images and containers"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/master/docker"
md_authors = "@manuelschneid3r"
md_bin_dependencies = "docker"
md_lib_dependencies = "docker"


class Plugin(PluginInstance, GlobalQueryHandler):

    def __init__(self):
        GlobalQueryHandler.__init__(self,
                                    id=md_id,
                                    name=md_name,
                                    description=md_description,
                                    defaultTrigger='d ',
                                    synopsis='<image tag|container name>')
        PluginInstance.__init__(self, extensions=[self])
        self.icon_urls_running = [f"file:{Path(__file__).parent}/running.png"]
        self.icon_urls_stopped = [f"file:{Path(__file__).parent}/stopped.png"]
        self.client = None

    def handleGlobalQuery(self, query):
        rank_items = []
        try:
            if not self.client:
                self.client = docker.from_env()

            for container in self.client.containers.list(all=True):
                if query.string in container.name:
                    # Create dynamic actions
                    if container.status == 'running':
                        actions = [Action("stop", "Stop container", lambda c=container: c.stop()),
                                   Action("restart", "Restart container", lambda c=container: c.restart())]
                    else:
                        actions = [Action("start", "Start container", lambda c=container: c.start())]
                    actions.extend([
                        Action("logs", "Logs",
                               lambda c=container.id: runTerminal("docker logs -f %s" % c, close_on_exit=False)),
                        Action("remove", "Remove (forced, with volumes)",
                               lambda c=container: c.remove(v=True, force=True)),
                        Action("copy-id", "Copy id to clipboard",
                               lambda id=container.id: setClipboardText(id))
                    ])

                    rank_items.append(RankItem(
                        item=StandardItem(
                            id=container.id,
                            text="%s (%s)" % (container.name, ", ".join(container.image.tags)),
                            subtext="Container: %s" % container.id,
                            iconUrls=self.icon_urls_running if container.status == 'running' else self.icon_urls_stopped,
                            actions=actions
                        ),
                        score=len(query.string)/len(container.name)
                    ))

            for image in reversed(self.client.images.list()):
                for tag in sorted(image.tags, key=len):  # order by resulting score
                    if query.string in tag:
                        rank_items.append(RankItem(
                            item=StandardItem(
                                id=image.short_id,
                                text=", ".join(image.tags),
                                subtext="Image: %s" % image.id,
                                iconUrls=self.icon_urls_stopped,
                                actions=[Action("run", "Run with command: %s" % query.string,
                                                lambda i=image, s=query.string: client.containers.run(i, s)),
                                         Action("rmi", "Remove image", lambda i=image: i.remove())]
                            ),
                            score=len(query.string)/len(tag)
                        ))
        except Exception as e:
            warning(e)
            self.client = None

        return rank_items
