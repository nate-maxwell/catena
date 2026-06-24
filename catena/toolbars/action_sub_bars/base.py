from pathlib import Path
from typing import Callable

from PySide6TK import QtWidgets
from PySide6TK import QtWrappers


class ActionToolbar(QtWrappers.Toolbar):
    """A convenience class with some pre-plugged values."""

    def __init__(
        self,
        toolbar_name: str,
        parent: QtWidgets.QWidget,
        image_path: Path,
    ) -> None:
        self.image_path = image_path
        super().__init__(
            toolbar_name, default_button_resolution=[40, 40], parent=parent
        )

    def add_action_button(self, label: str, action: Callable) -> None:
        self.add_toolbar_command(
            label, command=lambda: action(), image_path=self.image_path
        )
