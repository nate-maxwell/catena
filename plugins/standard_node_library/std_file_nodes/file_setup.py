import logging
from typing import Callable

from PySide6TK import Resources

from catena import api
from catena.toolbars import actions
from std_file_nodes.read import ReadNode
from std_file_nodes.write import WriteNode

logger = logging.getLogger(__name__)

CATEGORY = "Graph"


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_BLACK_40X40)


def _add_cmd(cmd: Callable, label: str) -> None:
    api.add_shelf_command(CATEGORY, cmd, label, Resources.BUTTON_BLACK_40X40)


def build_shelf() -> None:
    logger.info("Building std file shelf...")

    _add_cmd(lambda: actions.GraphActions.action_save(), "Save")
    _add_cmd(lambda: actions.GraphActions.action_write_files(), "Pub\nFiles")
    api.add_seperator_to_shelf(CATEGORY)
    _add_cmd(lambda: actions.GraphActions.action_undo(), "Undo")
    _add_cmd(lambda: actions.GraphActions.action_redo(), "Redo")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(ReadNode, "Read")
    _add_node(WriteNode, "Write")


def build_registry() -> None:
    logger.info("Registering std file nodes...")
    api.register_node(CATEGORY, ReadNode)
    api.register_node(CATEGORY, WriteNode)


def initialize() -> None:
    build_shelf()
    build_registry()
