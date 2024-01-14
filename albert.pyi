"""
# Albert Python interface v2.2


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

md_id                                | Identifier overwrite. [a-zA-Z0-9_]. Note: This variable is attached at runtime 
                                     | if it is unset and defaults to the module name.
md_license: str                      | Short form e.g. MIT or BSD-2
md_url: str                          | Browsable source, issues etc
md_authors: [str|List(str)]          | The authors. Preferably using mentionable Github usernames.
md_bin_dependencies: [str|List(str)] | Required executable(s). Have to match the name of the executable in $PATH.
md_lib_dependencies: [str|List(str)] | Required Python package(s). Have to match the PyPI package name.
md_credits: [str|List(str)]          | Third party credit(s) and license notes


## The Plugin class

The plugin class is the entry point for a Python plugin. It is instantiated on plugin initialization and has to subclass
PluginInstance. Implement extensions by subclassing _one_ extension class (TriggerQueryHandler etc…) provided by the
built-in `albert` module and pass the list of your extensions to the PluginInstance init function. Due to the
differences in type systems multiple inheritance of extensions is not supported. (Python does not support virtual
inheritance, which is used in the C++ space to inherit from 'Extension').

Changes in 2.1

 - Add PluginInstance.readConfig
 - Add PluginInstance.writeConfig
 - Add PluginInstance.configWidget

Changes in 2.2:

 - PluginInstance.configWidget supports 'label'
 - __doc__ is not used anymore, since 0.23 drops long_description metadata
 - md_maintainers not used anymore
 - md_authors new optional field
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
    """https://albertlauncher.github.io/reference/classalbert_1_1PluginInstance.html"""

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

    def readConfig(self, key: str, type: type[str|int|float|bool]) -> str|int|float|bool|None:
        """
        Read a config value from the Albert settings.
        Note: Due to limitations of QSettings on some platforms the type may be lost, therefore the type expected has to
        be passed.

        Returns:
             The requested value or None if the value does not exist or errors occurred.
        """

    def writeConfig(self, key: str, value: str|int|float|bool):
        """Write a config value to the Albert settings."""

    def configWidget(self) -> List[dict]:
        """
        **Descriptive config widget factory.**

        Define a static config widget using a list of dicts, each defining a row in the resulting form layout. Each dict
        must contain key 'type' having one of the supported types specified below. Each type may define further
        keys.

        **A note on 'widget_properties'**

        This is a dict setting the widget properties of a QWidget or one of its derived classes. See Qt documentation
        for a particular class. Note that due to the restricted type conversion only properties of type
        str|int|float|bool are settable.

        **Supported row 'type's**

        * 'label' (since 2.2)

          Display text spanning both columns. Additional keys:

          - 'text': The text to display
          - 'widget_properties': https://doc.qt.io/qt-6/qlabel.html.

        * 'checkbox'

          A form layout item to edit boolean properties. Additional keys:

          - 'label': The text displayed in front of the the editor widget.
          - 'property': The name of the property that will be set on changes.
          - 'widget_properties': https://doc.qt.io/qt-6/qcheckbox.html

        * 'lineedit'

          A form layout item to edit string properties. Additional keys:

          - 'label': The text displayed in front of the the editor widget.
          - 'property': The name of the property that will be set on changes.
          - 'widget_properties': https://doc.qt.io/qt-6/qlineedit.html

        * 'combobox'

          A form layout item to set string properties using a list of options. Additional keys:

          - 'label': The text displayed in front of the the editor widget.
          - 'property': The name of the property that will be set on changes.
          - 'items': The list of strings used to populate the combobox.
          - 'widget_properties': https://doc.qt.io/qt-6/qcombobox.html

        * 'spinbox'

          A form layout item to edit integer properties. Additional keys:

          - 'label': The text displayed in front of the the editor widget.
          - 'property': The name of the property that will be set on changes.
          - 'widget_properties': https://doc.qt.io/qt-6/qspinbox.html

        * 'doublespinbox'

          A form layout item to edit float properties. Additional keys:

          - 'label': The text displayed in front of the the editor widget.
          - 'property': The name of the property that will be set on changes.
          - 'widget_properties': https://doc.qt.io/qt-6/qdoublespinbox.html

        Returns:
            A list of dicts, describing a form layout as defined above.
        """

class Action:
    """https://albertlauncher.github.io/reference/classalbert_1_1Action.html"""

    def __init__(self,
                 id: str,
                 text: str,
                 callable: Callable):
        ...


class Item(ABC):
    """https://albertlauncher.github.io/reference/classalbert_1_1Item.html"""

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
        """See https://albertlauncher.github.io/reference/classalbert_1_1IconProvider.html"""

    @abstractmethod
    def actions(self) -> List[Action]:
        ...


class StandardItem(Item):
    """https://albertlauncher.github.io/reference/structalbert_1_1StandardItem.html"""

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
    """https://albertlauncher.github.io/reference/classalbert_1_1Extension.html"""

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
    """https://albertlauncher.github.io/reference/classalbert_1_1FallbackHandler.html"""

    @abstractmethod
    def fallbacks(self, query: str ) ->List[Item]:
        ...


class TriggerQuery(ABC):
    """https://albertlauncher.github.io/reference/classalbert_1_1TriggerQueryHandler_1_1TriggerQuery.html"""

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
    """https://albertlauncher.github.io/reference/classalbert_1_1TriggerQueryHandler.html"""

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
    """https://albertlauncher.github.io/reference/classalbert_1_1RankItem.html"""

    def __init__(self, item: Item, score: float):
        ...

    item: Item
    score: float


class GlobalQuery(ABC):
    """https://albertlauncher.github.io/reference/classalbert_1_1GlobalQueryHandler_1_1GlobalQuery.html"""

    @property
    def string(self) -> str:
        ...

    @property
    def isValid(self) -> bool:
        ...


class GlobalQueryHandler(TriggerQueryHandler):
    """https://albertlauncher.github.io/reference/classalbert_1_1GlobalQueryHandler.html"""

    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 synopsis: str = '',
                 defaultTrigger: str = f'{id} ',
                 allowTriggerRemap: str = true,
                 supportsFuzzyMatching: bool = False):
        ...

    @abstractmethod
    def handleGlobalQuery(self, query: GlobalQuery) -> List[RankItem]:
        ...

    def applyUsageScore(self, rank_items:  List[RankItem]):
        ...

    def handleTriggerQuery(self, query: TriggerQuery):
        ...


class IndexItem:
    """https://albertlauncher.github.io/reference/classalbert_1_1IndexItem.html"""

    def __init__(self, item: AbstractItem, string: str):
        ...

    item: AbstractItem
    string: str


class IndexQueryHandler(GlobalQueryHandler):
    """https://albertlauncher.github.io/reference/classalbert_1_1IndexQueryHandler.html"""

    @abstractmethod
    def updateIndexItems(self):
        ...

    def setIndexItems(self, indexItems: List[RankItem]):
        ...

    def handleGlobalQuery(self, query: GlobalQuery) -> List[RankItem]:
        ...


class Notification:

    def __init__(self, title: str, subtitle: str = '', text: str = ''):
        ...


def debug(arg: Any):
    """Module attached attribute"""


def info(arg: Any):
    """Module attached attribute"""


def warning(arg: Any):
    """Module attached attribute"""


def critical(arg: Any):
    """Module attached attribute"""


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

