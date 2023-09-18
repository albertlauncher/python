from albert import (
    PluginInstance,
    TriggerQuery,
    TriggerQueryHandler,
    Action,
    StandardItem,
    Item,
    setClipboardText,
    setClipboardTextAndPaste
)
from PySide6 import QtDBus

md_iid = "2.0"
md_version = "1.0"
md_name = "Klipper"
md_description = "Access Klipper clipboard history"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/master/locate"
md_maintainers = "@hmnd"
md_bin_dependencies = ["klipper"]
md_lib_dependencies = ["PySide6"]


class Klipper:
    bus: QtDBus.QDBusConnection
    bus_interface: QtDBus.QDBusInterface

    def __init__(self) -> None:
        self.bus = QtDBus.QDBusConnection.sessionBus()
        self.bus_interface = QtDBus.QDBusInterface(
            "org.kde.klipper",
            "/klipper",
            "org.kde.klipper.klipper",
            self.bus,
        )

    def getClipboardHistory(self) -> list[str]:
        return self.bus_interface.call("getClipboardHistoryMenu").arguments()[0]

    def setClipboardContents(self, text: str) -> None:
        self.bus_interface.call("setClipboardContents", text)


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        TriggerQueryHandler.__init__(
            self,
            id=md_id,  # noqa: F821
            name=md_name,
            description=md_description,
            synopsis="<filter>",
            defaultTrigger="kp",
        )
        self.iconUrls = ["xdg:klipper"]
        self.klipper = Klipper()
        PluginInstance.__init__(self, extensions=[self])

    def handleTriggerQuery(self, query: TriggerQuery):
        items: list[Item] = []
        query_str = query.string.strip()

        history = self.klipper.getClipboardHistory()

        for idx, item in enumerate(history):
            if not item.startswith("▨") and (
                not query_str or query_str.lower() in item.lower()
            ):
                items.append(
                    StandardItem(
                        id=f"klipper-item-{idx}",
                        iconUrls=["xdg:klipper"],
                        text=item,
                        actions=[
                            Action(
                                "copy",
                                "Copy",
                                lambda item=item: (setClipboardText(item)),
                            ),
                            Action(
                                "paste",
                                "paste",
                                lambda item=item: (setClipboardTextAndPaste(item)),
                            ),
                        ],
                    )
                )
        query.add(items)
