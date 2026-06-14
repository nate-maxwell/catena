"""
Status bar at the bottom of the application.

This status bar is not meant to allow users to change settings, but rather
simply display application data and preference values.
"""

from pathlib import Path

import broker
from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

from catena import __version__
from catena.core import namespace


class StatusBar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__("StatusBar", parent)
        broker.register_subscriber(namespace.FILE_CHANGED, self._update_file_name)

    def build(self) -> None:
        unsaved_path = Path(Path.home(), "Unsaved.cg")
        self.lbl_current_path = QtWidgets.QLabel(unsaved_path.as_posix())
        self.addWidget(self.lbl_current_path)

        self.addWidget(QtWrappers.HorizontalSpacer())
        self.addWidget(QtWrappers.VerticalSpacer(16))

        self.lbl_nonsense = QtWidgets.QLabel("Catena Engine Initialized")
        self.addWidget(self.lbl_nonsense)

        self.add_line()

        version_string = f"Version: {__version__.version_str}"
        self.lbl_version = QtWidgets.QLabel(version_string)
        self.addWidget(self.lbl_version)

        self.addWidget(QtWrappers.HorizontalSpacer(12))

    def add_line(self) -> None:
        width = 16
        self.add_toolbar_separator(width)
        self.addWidget(QtWrappers.VerticalLine())
        self.add_toolbar_separator(width)

    def _update_file_name(self, file_path: Path) -> None:
        self.lbl_current_path.setText(file_path.as_posix())
