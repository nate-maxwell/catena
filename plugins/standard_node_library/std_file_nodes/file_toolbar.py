from typing import Callable

from PySide6TK import Resources

from catena import api
from catena.toolbars import actions

from std_file_nodes.read import ReadNode
from std_file_nodes.write import WriteNode


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_toolbar("Graph", node, label, Resources.BUTTON_BLACK_40X40)


def _add_cmd(cmd: Callable, label: str) -> None:
    api.add_toolbar_command("Graph", cmd, label, Resources.BUTTON_BLACK_40X40)


def build_shelf() -> None:
    _add_cmd(lambda: actions.GraphActions.action_save(), "Save")
    _add_cmd(lambda: actions.GraphActions.action_write_files(), "Pub\nFiles")

    api.add_seperator_to_toolbar("Graph")

    _add_cmd(lambda: actions.GraphActions.action_undo(), "Undo")
    _add_cmd(lambda: actions.GraphActions.action_redo(), "Redo")

    api.add_seperator_to_toolbar("Graph")

    _add_node(ReadNode, "Read")
    _add_node(WriteNode, "Write")
