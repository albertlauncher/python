#!/usr/bin/env python3

"""
Albert Python interface specification v1.0

A Python plugin module is required to have the metadata described below and contain a
class named `Plugin` which will be instantiated when the plugin is loaded.


# Metadata

Mandatory metadata variables:

md_iid: str             Interface version (<major>.<minor>)
md_version: str         Plugin version (<major>.<minor>)
md_name: str            Human readable name
md_description: str     A brief, imperative description. (Like "Launch apps" or "Open files")

Optional metadata variables:

md_id                                   Identifier overwrite. [a-zA-Z0-9_]. Defaults to module name.
                                        Note `__name__` gets `albert.` prepended to avoid conflicts.
__doc__                                 The docstring of the module is used as long description/readme of the extension.
md_license: str                         Short form e.g. BSD-2-Clause or GPL-3.0
md_url: str                             Browsable source, issues etc
md_maintainers: [str|List(str)]         Active maintainer(s). Preferrably using mentionable Github usernames.
md_bin_dependencies: [str|List(str)]    Required executable(s). Have to match the name of the executable in $PATH.
md_lib_dependencies: [str|List(str)]    Required Python package(s). Have to match the PyPI package name.
md_credits: [str|List(str)]             Third party credit(s) and license notes


# The Plugin class

* The plugin class is the entry point for a plugin and instantiated on plugin initialization.
* Implement extensions by subclassing (one!) extension class provided by the built-in `albert` module.
  Due to the differences in type systems multiple inheritance of extensions is not supported.
  If the Plugin class inherits an extension it will be automatically registered.
* Define an "extensions() -> List[Extension]" instance function if you want to provide multiple extensions.
* Define initialize() and/or finalize() instance functions if needed.
  Do not use the constructor, since PyBind11 imposes some inconvenient boilerplate on them.
"""


from enum import Enum
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Union

class Action:
    """Action object for items."""
    def __init__(self,
                 id: str,
                 text: str,
                 callable: Callable):
        """
        Args:
            id: The identifier of the action
            text: The title of the action
            callable: The callable invoked on activation
        """


class AbstractItem:
    """The abstract item base class. Serves as result item. Represents albert::Item interface class."""


class Item(AbstractItem):
    """Standard result item. Represents albert::StandardItem."""

    def __init__(self,
                 id: str = '',
                 text: str = '',
                 subtext: str = '',
                 completion: Optional[str] = '',
                 icon: List[str] = [],
                 actions: List[Action] = []):
        ...

    id: str
    """Per extension unique identifier. Must not be empty."""

    text: str
    """The primary text of the item."""

    subtext: str
    """The secondary text of the item. This text should have informative character."""

    completion: str
    """
    The completion string of the item. This string will be used to replace the
    input line when the user hits the Tab key on an item. Note that the
    semantics may vary depending on the context.
    """

    icon: List[str]
    """
    Icon urls used for the icon lookup. Supported url schemes:
    * 'xdg:<icon-name>' performs freedesktop icon theme specification lookup (linux only).
    * 'qfip:<path>' uses QFileIconProvider to get the icon for the file.
    * ':<path>' is a QResource path.
    * '<path>' is interpreted as path to a local image file.
    """

    actions: List[Action]
    """The actions of the item."""


class Extension:
    """Abstract bae class for all extensions."""

    @abstractmethod
    def id(self) -> str:
        """The unique identifier of the extension."""

    @abstractmethod
    def name(self) -> str:
        """The human readable name of the extension."""

    @abstractmethod
    def description(self) -> str:
        """Brief description of the service provided."""


class FallbackHandler(Extension):
    """Base class for a fallback providing extensions."""
    @abstractmethod
    def fallbacks(self, query: str) -> List[AbstractItem]:
        """Implement to handle the fallback query."""


class TriggerQuery:
    """Represents a triggered, exclusive query execution."""

    @property
    def trigger(self) -> str:
        """The trigger that has been used to start this extension."""

    @property
    def string(self) -> str:
        """The actual query string (without the trigger)."""

    @property
    def isValid(self) -> bool:
        """This flag indicates that this the query is still valid. Cancel query processing if it is not."""

    @overload
    def add(self, item: AbstractItem):
        """Add a single result item."""

    @overload
    def add(self, item: List[AbstractItem]):
        """Add a list of result items."""


class TriggerQueryHandler(Extension):
    """Base class for a triggered query handling extensions."""

    @abstractmethod
    def synopsis(self) -> str:
        """Implement to return a synopsis, displayed on empty query. Defaults to empty."""

    @abstractmethod
    def defaultTrigger(self) -> str:
        """Implement to set a default trigger. Defaults to Extension::id()."""

    @abstractmethod
    def allowTriggerRemap(self) -> bool:
        """Implement to set trigger remapping permissions. Defaults to false."""

    @abstractmethod
    def handleTriggerQuery(self, query: TriggerQuery) -> None:
        """Implement to handle the triggered query."""


class GlobalQuery:
    """Represents a triggered, exclusive query execution."""

    @property
    def string(self) -> str:
        """The actual query string (without the trigger)."""

    @property
    def isValid(self) -> bool:
        """This flag indicates that this the query is still valid. Cancel query processing if it is not."""


class RankItem:
    """Result item with score for use in GlobalQueryHandler."""

    def __init__(self, item: AbstractItem, score: float):
        ...

    item: AbstractItem
    """The result item."""

    score: float
    """The score of the item (0,1]. No checks applied for performance."""


class GlobalQueryHandler(Extension):
    """Base class for a global query handling extensions."""

    @abstractmethod
    def handleGlobalQuery(self, query: GlobalQuery) -> List[RankItem]:
        """Implement to handle the global query."""


class QueryHandler(TriggerQueryHandler, GlobalQueryHandler):
    """
    Convenience base class that combines Trigger- and GlobalQueryHandler. Implements `handleTriggerQuery`
    by getting, sorting and adding the results of the handleGlobalQuery to the query.
    """

    def handleTriggerQuery(self, query: TriggerQuery) -> None:
        """Calls `handleGlobalQuery` and sorts and adds the results to the query."""


class IndexItem:
    """Index item with index string for use in IndexQueryHandler."""

    def __init__(self, item: AbstractItem, string: str):
        ...

    item: AbstractItem
    """The indexed item."""

    string: str
    """The index string used to look up this item."""


class IndexQueryHandler(QueryHandler):
    """
    Convenience base class that combines maintains an index and does matching and scoring for you.
    """

    def handleGlobalQuery(self, query: GlobalQuery) -> List[RankItem]:
        """Handles a global query by using the internal index."""

    def setIndexItems(self, indexItems: List[RankItem]) -> None:
        """Handles a global query by using the internal index."""

    @abstractmethod
    def updateIndexItems(self) -> None:
        """Implement to populate the index. Use `setIndexItems`."""


def debug(arg: Any) -> None:
    """
    Log a message to stdout at the "debug" log level. Note that debug is
    effectively a NOP in release builds
    Args:
        arg: The object to be logged.
    """


def info(arg: Any) -> None:
    """
    Log a message to stdout at the "info" log level.
    Args:
        arg: The object to be logged.
    """


def warning(arg: Any) -> None:
    """
    Log a message to stdout at the "warning" log level.
    Args:
        arg: The object to be logged.
    """


def critical(arg: Any) -> None:
    """
    Log a message to stdout at the "critical" log level.
    Args:
        arg: The object to be logged.
    """


def cacheLocation() -> str:
    """
    Returns:
        The writable cache location of the app.
    """


def configLocation() -> str:
    """
    Returns:
        The writable config location of the app.
    """


def dataLocation() -> str:
    """
    Returns:
        The writable data location of the app.
    """


def setClipboardText(text: str='') -> None:
    """
    Set the system clipboard text.
    Args:
        text: The text used to set the clipboard
    """


def openUrl(url:str='') -> None:
    """
    Open an URL using QDesktopServices::openUrl.
    Args:
        url: The URL to open
    """


def runDetachedProcess(cmdln: List[str] = [], workdir: str = '') -> None:
    """
    Run a detached process.
    Args:
        cmdln: The commandline to run in the terminal (argv)
        workdir: The working directory used to run the terminal
    """


def runTerminal(script: str='', workdir: str = '', close_on_exit: bool = False) -> None:
    """
    Run a script the user shell in the user specified terminal.
    Args:
        script: The script to be executed.
        workdir: The working directory used to run the process
        close_on_exit: Close the terminal on exit. Otherwise exec $SHELL.
    """


def sendTrayNotification(title: str='', msg: str = '', ms: int = 10000) -> None:
    """
    Send a tray notification.
    Args:
        title: The notification title
        msg: The notification body
        ms: The display time (if supported by the system)
    """

