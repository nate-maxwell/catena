import logging
from pathlib import Path
from typing import Callable

from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena import api
from catena.nodes.node_gui import CatenaNode
from catena.toolbars.action_sub_bars.base import ActionToolbar
from catena.toolbars.action_sub_bars.switcher import ToolbarSwitcher

logger = logging.getLogger(__name__)


class EditorActionToolbar(QtWrappers.Toolbar):
    """The primary toolbar with sub-toolbars inside a maya shelf-like tab switcher."""

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(
            "ActionsToolbar", default_button_resolution=[40, 40], parent=parent
        )
        self.switcher = ToolbarSwitcher(self)
        self.addWidget(self.switcher)
        self.toolbars: dict[str, ActionToolbar] = {}
        logger.info("Actions toolbar initialized")

    def add_command(
        self,
        toolbar: str,
        command: Callable,
        label: str,
        icon_path: Path = Resources.BUTTON_WHITE_40X40,
    ) -> None:
        if toolbar in self.toolbars:
            toolbar_ = self.toolbars[toolbar]
        else:
            logger.info(f"Constructing new toolbar: {toolbar}")
            toolbar_ = ActionToolbar(toolbar, self, Resources.BUTTON_BLACK_40X40)

            self.toolbars[toolbar] = toolbar_
            self.switcher.add_toolbar(toolbar, toolbar_)

        toolbar_.add_toolbar_command(label, command, icon_path)

    def add_node(
        self,
        toolbar: str,
        node: type[CatenaNode],
        label: str,
        icon_path: Path = Resources.BUTTON_WHITE_40X40,
    ) -> None:
        cmd = lambda: api.add_to_focussed(node)
        logger.info(f"Adding node {node.__name__} to toolbar {toolbar}")
        self.add_command(toolbar, cmd, label, icon_path)

    def add_seperator(self, toolbar: str) -> None:
        if toolbar not in self.toolbars:
            return

        logger.info(f"Adding separator to toolbar {toolbar}")
        self.toolbars[toolbar].add_toolbar_separator(12)
