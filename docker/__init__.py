"""
Docker wrapper (prototype)
"""

from albert import TermAction, FuncAction, ClipAction, Item
import docker
import pathlib

__title__ = "Docker"
__version__ = "0.4.1"
__triggers__ = "d "
__authors__ = "manuelschneid3r"
__py_deps__ = ["docker"]

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
        raise "Failed to initialize client."


def handleQuery(query):
    if query.isValid and query.isTriggered:

        query.disableSort()
        items = []

        for container in client.containers.list(all=True):

            # Create dynamic actions
            if container.status == 'running':
                actions = [
                    FuncAction("Stop container", lambda c=container: c.stop()),
                    FuncAction("Restart", lambda c=container: c.restart()),
                ]
            else:
                actions = [FuncAction("Start", lambda c=container: c.start())]
            actions.extend([
                TermAction("Logs", "docker logs -f %s" % container.id,
                           behavior=TermAction.CloseBehavior.DoNotClose),
                FuncAction("Remove (forced, with volumes)", lambda c=container: c.remove(v=True, force=True)),
                ClipAction("Copy id to clipboard", container.id)
            ])

            item = Item(
                id=container.id,
                text="%s <i>%s</i>" % (container.name, ", ".join(container.image.tags)),
                subtext=container.id,
                icon=icon_running if container.status == 'running' else icon_stopped,
                actions=actions
            )

            items.append(item)

        for image in reversed(client.images.list()):
            item = Item(
                id=image.short_id,
                text=str(image.tags),
                subtext=image.id,
                icon=icon_stopped,
                actions=[
                    FuncAction("Run with command: %s" % query.string, lambda i=image: client.containers.run(i, query.string)),
                    FuncAction("Remove", lambda i=image: i.remove())
                ]
            )

            items.append(item)

        return items
