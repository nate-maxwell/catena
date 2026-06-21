from pathlib import Path
from typing import Callable

from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

from catena.nodes.graph_gui import GuiGraphView

TOOLBAR_CALLABLE = Callable[[GuiGraphView], None]


class ActionToolbar(QtWrappers.Toolbar):
    """A convenience class with some pre-plugged values."""

    def __init__(
        self,
        toolbar_name: str,
        parent: QtWidgets.QWidget,
        graph_view: GuiGraphView,
        image_path: Path,
    ) -> None:
        self.image_path = image_path
        self.graph_view = graph_view
        super().__init__(
            toolbar_name, default_button_resolution=[40, 40], parent=parent
        )

    def add_action_button(self, label: str, action: TOOLBAR_CALLABLE) -> None:
        self.add_toolbar_command(
            label, command=lambda: action(self.graph_view), image_path=self.image_path
        )
