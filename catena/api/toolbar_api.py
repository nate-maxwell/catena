from pathlib import Path
from typing import Callable

from PySide6TK import Resources

from catena.nodes.node_gui import CatenaNode
from catena.toolbars.actions_toolbar import EditorActionToolbar

__all__ = ["add_node_to_toolbar", "add_seperator_to_toolbar", "add_toolbar_command"]


_editor_actions_toolbar: EditorActionToolbar | None = None


def init_actions_toolbar_ref(toolbar: EditorActionToolbar | None = None) -> None:
    global _editor_actions_toolbar
    if toolbar is None:
        return

    _editor_actions_toolbar = toolbar


def add_toolbar_command(
    toolbar: str,
    command: Callable,
    label: str,
    icon_path: Path = Resources.BUTTON_WHITE_40X40,
) -> None:
    """
    Adds the given callable python command to the specified toolbar.

    Args:
        toolbar (str): The toolbar name to add the command to. If one by the given
            name is not found, one is constructed.
        command (Callable): The command to execute on button press.
        label (str): The button label.
        icon_path (pathlib.Path): The button icon. Defaults to the 40x40 white
            image box.

    Returns:

    """
    _editor_actions_toolbar.add_command(toolbar, command, label, icon_path)


def add_node_to_toolbar(
    toolbar: str,
    node: type[CatenaNode],
    label: str,
    icon_path: Path = Resources.BUTTON_WHITE_40X40,
) -> None:
    """
    Adds a node to the toolbar by the given name. If a toolbar cannot be found by
    that name, one is constructed and the button is added to that.

    Args:
        toolbar (str): The toolbar name to add the node to. If one by the given
            name is not found, one is constructed.
        node (type[CatenaNode]): The node to spawn on button press.
        label (str): The button label.
        icon_path (pathlib.Path): The button icon. Defaults to the 40x40 white
            image box.
    """
    _editor_actions_toolbar.add_node(toolbar, node, label, icon_path)


def add_seperator_to_toolbar(toolbar: str) -> None:
    """Add a spacing seperator to the toolbar of the given name."""
    _editor_actions_toolbar.add_seperator(toolbar)
