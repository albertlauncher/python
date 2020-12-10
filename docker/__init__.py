"""
Docker wrapper (prototype)
"""

from albertv0 import *
import os
import docker
import pathlib

__iid__ = "PythonInterface/v0.3"
__prettyname__ = "Docker"
__version__ = "0.1"
__trigger__ = "d "
__author__ = "manuelschneid3r"
__dependencies__ = ["docker"]


icon_running = str(pathlib.Path(__file__).parent / "running.png")
icon_stopped = str(pathlib.Path(__file__).parent / "stopped.png")

client = None

def initialize():
    global client
    client = docker.from_env()
    if client:
        return
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    if not client:
        raise "fcckit"


def build_container_item(container):
    item

def handleQuery(query):
    if query.isValid and query.isTriggered:

        query.disableSort()

        items = []

        for c in client.containers.list(all=True):

            # Create dynamic actions
            if c.status == 'running':
                actions = [
                    FuncAction("Stop container", lambda c=c: c.stop()),
                    FuncAction("Restart", lambda c=c: c.restart()),
                ]
            else:
                actions = [FuncAction("Start", lambda c=c: c.start())]
            actions.extend([
                TermAction("Logs", ["docker", "logs", "-f", c.id],
                           behavior=TermAction.CloseBehavior.DoNotClose),
                FuncAction("Remove (forced, with volumes)", lambda c=c: c.remove(v=True, force=True)),
                ClipAction("Copy id to clipboard", c.id)
            ])

            item = Item(
                id=c.id,
                text="%s <i>%s</i>" % (c.name, ", ".join(c.image.tags)),
                subtext=c.id,
                icon=icon_running if c.status == 'running' else icon_stopped,
                completion=query.rawString,
                actions=actions
            )

            items.append(item)

        for i in reversed(client.images.list()):
            item = Item(
                id=i.short_id,
                text=str(i.tags),
                subtext=i.id,
                icon=icon_stopped,
                completion=query.rawString,
                actions=[
                    FuncAction("Run with commmand: %s" % query.string, lambda i=i: client.containers.run(i, query.string)),
                    FuncAction("Remove", lambda i=i: i.remove())
                ]
            )

            items.append(item)

        return items
