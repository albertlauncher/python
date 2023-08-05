"""

# Albert Python interface v2.0


The Python interface is a subset of the internal C++ interface exposed to Python with some minor adjustments. A Python
plugin is required to contain the mandatory metadata and a plugin class, both described below. To get started read the
top level classes and function names in this file. Most of them are self explanatory. In case of questions see the C++
documentation at https://albertlauncher.github.io/reference/namespacealbert.html


## Mandatory metadata variables

md_iid: str         | Interface version (<major>.<minor>)
md_version: str     | Plugin version (<major>.<minor>)
md_name: str        | Human readable name
md_description: str | A brief, imperative description. (Like "Launch apps" or "Open files")


## Optional metadata variables:

md_id                                | Identifier overwrite. [a-zA-Z0-9_]. Defaults to module name.
__doc__                              | The docstring of the module is used as long description/readme of the extension.
md_license: str                      | Short form e.g. BSD-2-Clause or GPL-3.0
md_url: str                          | Browsable source, issues etc
md_maintainers: [str|List(str)]      | Active maintainer(s). Preferrably using mentionable Github usernames.
md_bin_dependencies: [str|List(str)] | Required executable(s). Have to match the name of the executable in $PATH.
md_lib_dependencies: [str|List(str)] | Required Python package(s). Have to match the PyPI package name.
md_credits: [str|List(str)]          | Third party credit(s) and license notes


## The Plugin class

The plugin class is the entry point for a Python plugin. It is instantiated on plugin initialization and has to subclass
PluginInstance. Implement extension(s) by subclassing _one_ extension class (TriggerQueryHandler etc…) provided by the
built-in `albert` module and pass the list of your extensions to the PluginInstance init function. Due to the
differences in type systems multiple inheritance of extensions is not supported. (Python does not support virtual
inheritance, which is used in the C++ space to inherit from 'Extension'). For more details see

"""


from abc import abstractmethod, ABC
from enum import Enum
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Union
from typing import overload


class PluginInstance(ABC):
    """https://albertlauncher.github.io/reference/classalbert_1_1_plugin_instance.html"""

    def __init__(self, extensions: List[Extension] = []):
        ...

    @property
    def id(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    @property
    def cacheLocation(self) -> pathlib.Path:
        ...

    @property
    def configLocation(self) -> pathlib.Path:
        ...

    @property
    def dataLocation(self) -> pathlib.Path:
        ...

    @property
    def extensions(self) -> List[Extension]:
        ...

    def initialize(self):
        ...

    def finalize(self):
        ...


class Action:
    """https://albertlauncher.github.io/reference/classalbert_1_1_action.html"""

    def __init__(self,
                 id: str,
                 text: str,
                 callable: Callable):
        ...


class Item(ABC):
    """https://albertlauncher.github.io/reference/classalbert_1_1_item.html"""

    @abstractmethod
    def id(self) -> str:
        ...

    @abstractmethod
    def text(self) -> str:
        ...

    @abstractmethod
    def subtext(self) -> str:
        ...

    @abstractmethod
    def inputActionText(self) -> str:
        ...

    @abstractmethod
    def iconUrls(self) -> List[str]:
        """See https://albertlauncher.github.io/reference/classalbert_1_1_icon_provider.html"""

    @abstractmethod
    def actions(self) -> List[Action]:
        ...


class StandardItem(Item):
    """https://albertlauncher.github.io/reference/structalbert_1_1_standard_item.html"""

    def __init__(self,
                 id: str = '',
                 text: str = '',
                 subtext: str = '',
                 iconUrls: List[str] = [],
                 actions: List[Action] = [],
                 inputActionText: Optional[str] = ''):
        ...

    id: str
    text: str
    subtext: str
    iconUrls: List[str]
    actions: List[Action]
    inputActionText: str


class Extension(ABC):
    """https://albertlauncher.github.io/reference/classalbert_1_1_extension.html"""

    @property
    def id(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...


class FallbackHandler(ABC):
    """https://albertlauncher.github.io/reference/classalbert_1_1_fallback_handler.html"""

    @abstractmethod
    def fallbacks(self, query: str ) ->List[Item]:
        ...


class TriggerQuery(ABC):
    """https://albertlauncher.github.io/reference/classalbert_1_1_trigger_query_handler_1_1_trigger_query.html"""

    @property
    def trigger(self) -> str:
        ...

    @property
    def string(self) -> str:
        ...

    @property
    def isValid(self) -> bool:
        ...

    @overload
    def add(self, item: Item):
        ...

    @overload
    def add(self, item: List[Item]):
        ...


class TriggerQueryHandler(Extension):
    """https://albertlauncher.github.io/reference/classalbert_1_1_trigger_query_handler.html"""

    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 synopsis: str = '',
                 defaultTrigger: str = f'{id} ',
                 allowTriggerRemap: str = true,
                 supportsFuzzyMatching: bool = False):
        ...

    @property
    def synopsis(self) -> str:
        ...

    @property
    def trigger(self) -> str:
        ...

    @property
    def defaultTrigger(self) -> str:
        ...

    @property
    def allowTriggerRemap(self) -> bool:
        ...

    @property
    def supportsFuzzyMatching(self) -> bool:
        ...

    @property
    def fuzzyMatching(self) -> bool:
        ...

    @fuzzyMatching.setter
    def setFuzzyMatching(self, enabled: bool):
        ...

    @abstractmethod
    def handleTriggerQuery(self, query: TriggerQuery):
        ...


class RankItem:
    """https://albertlauncher.github.io/reference/classalbert_1_1_rank_item.html"""

    def __init__(self, item: Item, score: float):
        ...

    item: Item
    score: float


class GlobalQuery(ABC):
    """https://albertlauncher.github.io/reference/classalbert_1_1_global_query_handler_1_1_global_query.html"""

    @property
    def string(self) -> str:
        ...

    @property
    def isValid(self) -> bool:
        ...


class GlobalQueryHandler(TriggerQueryHandler):
    """https://albertlauncher.github.io/reference/classalbert_1_1_global_query_handler.html"""

    @abstractmethod
    def handleGlobalQuery(self, query: GlobalQuery) -> List[RankItem]:
        ...

    def applyUsageScore(self, rank_items:  List[RankItem]):
        ...

    def handleTriggerQuery(self, query: TriggerQuery):
        ...


class IndexItem:
    """https://albertlauncher.github.io/reference/classalbert_1_1_index_item.html"""

    def __init__(self, item: AbstractItem, string: str):
        ...

    item: AbstractItem
    string: str


class IndexQueryHandler(GlobalQueryHandler):
    """https://albertlauncher.github.io/reference/classalbert_1_1_index_query_handler.html"""

    @abstractmethod
    def updateIndexItems(self):
        ...

    def setIndexItems(self, indexItems: List[RankItem]):
        ...

    def handleGlobalQuery(self, query: GlobalQuery) -> List[RankItem]:
        ...


def debug(arg: Any):...
def info(arg: Any):...
def warning(arg: Any):...
def critical(arg: Any):...


def setClipboardText(text: str=''):
    """
    Set the system clipboard text.
    Args:
        text: The text used to set the clipboard
    """


def setClipboardTextAndPaste(text: str=''):
    """
    Set the system clipboard text and paste to the front-most window
    Args:
        text: The text used to set the clipboard
    """


def openUrl(url: str = ''):
    """
    Open an URL using QDesktopServices::openUrl.
    Args:
        url: The URL to open
    """


def runDetachedProcess(cmdln: List[str] = [], workdir: str = ''):
    """
    Run a detached process.
    Args:
        cmdln: The commandline to run in the terminal (argv)
        workdir: The working directory used to run the terminal
    """


def runTerminal(script: str = '', workdir: str = '', close_on_exit: bool = False):
    """
    Run a script in the users shell and terminal.
    Args:
        script: The script to be executed.
        workdir: The working directory used to run the process
        close_on_exit: Close the terminal on exit. Otherwise exec $SHELL.
    """


def sendTrayNotification(title: str = '', msg: str = '', ms: int = 10000):
    """
    Send a tray notification.
    Args:
        title: The notification title
        msg: The notification body
        ms: The display time (if supported by the system)
    """

