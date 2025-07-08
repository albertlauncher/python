import albert as al
import subprocess as sp
import time

md_iid = "3.0"
md_version = "1.0"
md_name = "ClipHist"
md_description = "Access cliphist clipboard"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/cliphist"
md_authors = ["@ivomac"]
md_bin_dependencies = ["cliphist"]


def copy(item: str):
    """Copy an entry from cliphist to the clipboard."""
    clip_entry = sp.run(["cliphist", "decode"], input=item, stdout=sp.PIPE, text=True)

    al.setClipboardText(clip_entry.stdout)


def delete(item: str):
    """Delete an entry from cliphist."""
    sp.run(["cliphist", "delete"], input=item, text=True)


def wipe():
    """Delete all entries from cliphist."""
    sp.run(["cliphist", "wipe"], text=True)


class Plugin(al.PluginInstance, al.TriggerQueryHandler):
    iconUrls = ["xdg:clipboard"]

    def __init__(self):
        al.PluginInstance.__init__(self)
        al.TriggerQueryHandler.__init__(self)

    def defaultTrigger(self):
        return "ch "

    def handleTriggerQuery(self, query):
        for _ in range(5):
            time.sleep(0.02)
            if not query.isValid:
                return

        plug_id = self.id()

        matcher = al.Matcher(query.string)

        # Get the list of cliphist entries
        clip_history = sp.run(["cliphist", "list"], stdout=sp.PIPE, text=True).stdout

        # cliphist items are in the format:
        # <id>\t<approximate text>
        splits = [(item, *item.split("\t", 1)) for item in clip_history.strip().splitlines()]

        query.add(
            [
                al.StandardItem(
                    id=plug_id,
                    iconUrls=self.iconUrls,
                    text=text,
                    subtext=idx,
                    actions=[
                        al.Action("copy", "Copy", lambda u=item: copy(u)),
                        al.Action("delete", "Delete", lambda u=item: delete(u)),
                        al.Action("wipe", "Wipe", lambda: wipe()),
                    ],
                )
                for item, idx, text in splits
                if matcher.match(item)
            ]
        )
