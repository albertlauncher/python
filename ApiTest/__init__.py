"""This is a simple python template extension that should show the API in a comprehensible way.
Use the module docstring to provide a detailed description of the extension"""

from albertv0 import *
import os

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Api Test"
__version__ = "1.0"
__trigger__ = "test "
__author__ = "Manuel Schneider"
__dependencies__ = ["whatever"]

iconPath = iconLookup("albert")

# Can be omitted
def initialize():
    pass


# Can be omitted
def finalize():
    pass


def handleQuery(query):

    # Note that when storing a reference to query, e.g. in a closure, you must not use
    # query.isValid. Apart from the query beeing invalid anyway it will crash the appplication.
    # The Python type holds a pointer to the C++ type used for isValid(). The C++ type will be
    # deleted when the query is finished. Therfore getting isValid will result in a SEGFAULT.

    info(query.string)
    info(query.rawString)
    info(query.trigger)
    info(str(query.isTriggered))
    info(str(query.isValid))

    critical(query.string)
    warning(query.string)
    debug(query.string)
    debug(query.string)

    results = []

    item = Item()

    item.icon = iconPath
    item.text = 'Python item containing %s' % query.string
    item.subtext = 'Python description'
    item.completion = __trigger__ + 'Completion Harharhar'
    item.urgency = ItemBase.Notification  # Alert, Normal
    info(item.icon)
    info(item.text)
    info(item.subtext)
    info(item.completion)
    info(str(item.urgency))
    def function(): info(query.string)
    item.addAction(FuncAction("Print info", function))
    item.addAction(FuncAction("Print warning", lambda: warning(query.string)))
    results.append(item)

    item = Item(id="id",
                icon=os.path.dirname(__file__)+"/plugin.svg",
                text="This is the primary text",
                subtext="This is the subtext, some kind of description",
                completion=__trigger__ + 'Hellooohooo!',
                urgency=ItemBase.Alert,
                actions=[
                    FuncAction(text="FuncAction",
                               callable=lambda: critical(query.string)),
                    ClipAction(text="ClipAction",
                               clipboardText="blabla"),
                    UrlAction(text="UrlAction",
                              url="https://www.google.de"),
                    ProcAction(text="ProcAction",
                               commandline=["espeak", "hello"],
                               cwd="~"),  # optional
                    TermAction(text="TermAction",
                               commandline=["sleep", "5"],
                               cwd="~/git")  # optional
                ])
    results.append(item)

    return results
