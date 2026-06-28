from pathlib import Path
from typing import Callable
from typing import TYPE_CHECKING

import broker
from PySide6 import QtWidgets
from PySide6TK import Resources

from catena import appdata
from catena import namespace
from catena.nodes.node import CatenaNode
from catena.toolbars.menu_toolbar import MenuToolbar
from catena.toolbars.shelf_toolbar.actions_toolbar import EditorActionToolbar

if TYPE_CHECKING:
    from catena.client import CatenaEditor

__all__ = [
    "add_node_to_shelf",
    "add_seperator_to_shelf",
    "add_shelf_command",
    "add_menu",
    "add_toolbar_menu_item",
    "set_status",
    "reset_status",
]


# -----Editor Actions Toolbar--------------------------------------------------

_editor_actions_toolbar: EditorActionToolbar | None = None


def init_actions_toolbar_ref(toolbar: EditorActionToolbar | None = None) -> None:
    """
    Used by the client at startup to inject the actions toolbar which manages all
    node category and button toolbars.
    """
    global _editor_actions_toolbar
    if toolbar is None:
        return

    _editor_actions_toolbar = toolbar


def add_shelf_command(
    shelf: str,
    command: Callable,
    label: str,
    icon_path: Path = Resources.BUTTON_WHITE_40X40,
) -> None:
    """
    Adds the given callable python command to the specified shelf.

    Args:
        shelf (str): The shelf name to add the command to. If one by the given
            name is not found, one is constructed.
        command (Callable): The command to execute on button press.
        label (str): The button label.
        icon_path (pathlib.Path): The button icon. Defaults to the 40x40 white
            image box.

    Returns:

    """
    _editor_actions_toolbar.add_command(shelf, command, label, icon_path)


def add_node_to_shelf(
    shelf: str,
    node: type[CatenaNode],
    label: str,
    icon_path: Path = Resources.BUTTON_WHITE_40X40,
) -> None:
    """
    Adds a node to the toolbar by the given name. If a toolbar cannot be found by
    that name, one is constructed and the button is added to that.

    Args:
        shelf (str): The shelf name to add the node to. If one by the given
            name is not found, one is constructed.
        node (type[CatenaNode]): The node to spawn on button press.
        label (str): The button label.
        icon_path (pathlib.Path): The button icon. Defaults to the 40x40 white
            image box.
    """
    _editor_actions_toolbar.add_node(shelf, node, label, icon_path)


def add_seperator_to_shelf(shelf: str) -> None:
    """Add a spacing seperator to the shelf of the given name."""
    _editor_actions_toolbar.add_seperator(shelf)


# -----Client Menu Toolbar-----------------------------------------------------

_menu_toolbar: MenuToolbar | None = None


def null(*args) -> None:
    return


def init_menu_toolbar_ref(toolbar: MenuToolbar | None = None) -> None:
    """Used by the client at startup to inject the menu toolbar."""
    global _menu_toolbar
    if toolbar is None:
        return

    _menu_toolbar = toolbar


def add_menu(label: str) -> QtWidgets.QMenu:
    """
    Adds a menu to the menu toolbar using the given label.
    Returns the QMenu object that was created.

    This QMenu object can be passed into api.add_menu_command to add a callable
    command to this returned submenu.

    If one already exists by the given label, it is returned, otherwise it is
    created instead.
    """
    return _menu_toolbar.create_menu(label)


def add_toolbar_menu_item(
    submenu: QtWidgets.QMenu, cmd_name: str, cmd: Callable = null
) -> None:
    """
    Adds a callable command to the given submenu, with a label entry using
    the given cmd_name.

    A dummy command that does nothing is used as the default command.

    Args:
        submenu (QtWidgets.QMenu): The submenu to add the item to.
        cmd_name (str): The label to add as an entry to invoke the command.
        cmd (Callable): The callable command to invoke on selection.
    Example:
        >>> from catena import api
        >>> menu = api.add_menu("My Menu")
        >>> api.add_toolbar_menu_item(menu, "Print", lambda: print("hello world"))
    """
    _menu_toolbar.add_menu_command(submenu, cmd_name, cmd)


# -----Client Status- Toolbar--------------------------------------------------


def set_status(status: str) -> None:
    """Sets the status on the bottom status bar to the given value."""
    broker.emit(namespace.STATUS_CHANGED, status=status)


def reset_status() -> None:
    """
    Resets the status on teh bottom status bar to the default engine running
    status.
    """
    broker.emit(namespace.STATUS_CHANGED, status=appdata.STATUS_IDLE)
