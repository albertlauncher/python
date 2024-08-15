# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

from pathlib import Path

import docker
from albert import *

md_iid = "2.3"
md_version = "3.0"
md_name = "Docker"
md_description = "Manage docker images and containers"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/docker"
md_authors = "@manuelschneid3r"
md_bin_dependencies = "docker"
md_lib_dependencies = "docker"


class Plugin(PluginInstance, TriggerQueryHandler):
    # Global query handler not applicable, queries take seconds sometimes

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(
            self, self.id, self.name, self.description,
            defaultTrigger='d ',
            synopsis='<image tag|container name>'
        )
        self.icon_urls_running = [f"file:{Path(__file__).parent}/running.png"]
        self.icon_urls_stopped = [f"file:{Path(__file__).parent}/stopped.png"]
        self.client = None

    def handleTriggerQuery(self, query):
        items = []

        if not self.client:
            try:
                self.client = docker.from_env()
            except Exception as e:
                items.append(StandardItem(
                    id='except',
                    text="Failed starting docker client",
                    subtext=str(e),
                    iconUrls=self.icon_urls_running,
                ))
                return items

        try:
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
                               lambda c=container.id: runTerminal("docker logs -f %s ; exec $SHELL" % c)),
                        Action("remove", "Remove (forced, with volumes)",
                               lambda c=container: c.remove(v=True, force=True)),
                        Action("copy-id", "Copy id to clipboard",
                               lambda id=container.id: setClipboardText(id))
                    ])

                    items.append(StandardItem(
                        id=container.id,
                        text="%s (%s)" % (container.name, ", ".join(container.image.tags)),
                        subtext="Container: %s" % container.id,
                        iconUrls=self.icon_urls_running if container.status == 'running' else self.icon_urls_stopped,
                        actions=actions
                    ))

            for image in reversed(self.client.images.list()):
                for tag in sorted(image.tags, key=len):  # order by resulting score
                    if query.string in tag:
                        items.append(StandardItem(
                            id=image.short_id,
                            text=", ".join(image.tags),
                            subtext="Image: %s" % image.id,
                            iconUrls=self.icon_urls_stopped,
                            actions=[
                                # Action("run", "Run with command: %s" % query.string,
                                #        lambda i=image, s=query.string: client.containers.run(i, s)),
                                Action("rmi", "Remove image", lambda i=image: i.remove())
                            ]
                        ))
        except Exception as e:
            warning(str(e))
            self.client = None

        query.add(items)
