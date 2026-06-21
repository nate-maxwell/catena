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
from catena import appdata
from catena import namespace


class StatusBar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__("StatusBar", parent)
        self._register_subscribers()

    def build(self) -> None:
        unsaved_path = Path(Path.home(), "Unsaved.cg")
        self.lbl_current_path = QtWidgets.QLabel(unsaved_path.as_posix())
        self.addWidget(self.lbl_current_path)

        self.addWidget(QtWrappers.HorizontalSpacer())
        self.addWidget(QtWrappers.VerticalSpacer(16))

        self.lbl_status = QtWidgets.QLabel(appdata.STATUS_IDLE)
        self.addWidget(self.lbl_status)

        self.add_line()

        version_string = f"Version: {__version__}"
        self.lbl_version = QtWidgets.QLabel(version_string)
        self.addWidget(self.lbl_version)

        self.addWidget(QtWrappers.HorizontalSpacer(12))

    def add_line(self) -> None:
        width = 16
        self.add_toolbar_separator(width)
        self.addWidget(QtWrappers.VerticalLine())
        self.add_toolbar_separator(width)

    def _register_subscribers(self) -> None:
        broker.register_subscriber(namespace.FILE_CHANGED, self._update_file)
        broker.register_subscriber(namespace.STATUS_CHANGED, self._update_status)

    def _update_file(self, file_path: Path) -> None:
        self.lbl_current_path.setText(file_path.as_posix())

    def _update_status(self, status: str) -> None:
        self.lbl_status.setText(status)
