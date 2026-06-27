import logging
from pathlib import Path

from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena import api
from catena.nodes.node_gui import CatenaNode
from catena.toolbars.action_sub_bars.base import ActionToolbar
from catena.toolbars.action_sub_bars.switcher import ToolbarSwitcher

logger = logging.getLogger(__name__)


class NewToolbar(ActionToolbar):

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__("TransformToolbar", parent, Resources.BUTTON_GREEN_40X40)


class EditorActionToolbar(QtWrappers.Toolbar):
    """The primary toolbar with sub-toolbars inside a maya shelf-like tab switcher."""

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        # self.toolbars: dict[str, ActionToolbar] = {
        #     "Graph": GraphToolbar(self),
        #     "Convert": ConvertToolbar(self),
        #     "Flood Fill": FloodFillToolbar(self),
        #     "Generators": GeneratorToolbar(self),
        #     "Math": MathToolbar(self),
        #     "Modifier": ModifierToolbar(self),
        #     "Subgraph": SubgraphToolbar(self),
        #     "Transform": TransformToolbar(self),
        # }
        self.toolbars: dict[str, ActionToolbar] = {}

        super().__init__(
            "ActionsToolbar", default_button_resolution=[40, 40], parent=parent
        )
        logger.info("Actions toolbar initialized")

    def build(self) -> None:
        self.switcher = ToolbarSwitcher(self)

        for k, v in self.toolbars.items():
            self.switcher.add_toolbar(k, v)

        self.addWidget(self.switcher)

    def add_node(
        self,
        toolbar: str,
        node: type[CatenaNode],
        label: str,
        icon_path: Path = Resources.BUTTON_WHITE_40X40,
    ) -> None:
        if toolbar in self.toolbars:
            toolbar_ = self.toolbars[toolbar]
        else:
            logger.info(f"Constructing new toolbar: {toolbar}")
            toolbar_ = ActionToolbar(toolbar, self, icon_path)

            self.toolbars[toolbar] = toolbar_
            self.switcher.add_toolbar(toolbar, toolbar_)

        try:
            cmd = lambda: api.add_to_focussed(node)
            toolbar_.add_action_button(label, cmd)

            logger.info(f"Adding node {node.__name__} to toolbar {toolbar}")
        except Exception as e:
            logger.error(f"Error creating toolbar command: {e}")

    def add_seperator(self, toolbar: str) -> None:
        if toolbar not in self.toolbars:
            return

        self.toolbars[toolbar].add_toolbar_separator(12)
