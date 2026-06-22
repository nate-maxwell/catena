import logging
from typing import Optional

from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets


class QtLogHandler(logging.Handler, QtCore.QObject):
    log_record = QtCore.Signal(logging.LogRecord)

    def __init__(self) -> None:
        logging.Handler.__init__(self)
        QtCore.QObject.__init__(self)

    def emit(self, record: logging.LogRecord) -> None:
        self.log_record.emit(record)


class LogWidget(QtWidgets.QWidget):
    LEVEL_COLORS = {
        logging.DEBUG: "#888888",
        logging.INFO: "#dddddd",
        logging.WARNING: "#f0c040",
        logging.ERROR: "#e05050",
        logging.CRITICAL: "#ff4444",
    }

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:

        super().__init__(parent)
        self._text = QtWidgets.QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setFont(QtGui.QFont("Courier New", 9))

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._text)

    def append_record(self, record: logging.LogRecord) -> None:
        color = self.LEVEL_COLORS.get(record.levelno, "#dddddd")

        # Format: [LEVEL]  message
        line = f'<span style="color:{color}">[{record.levelname:<8}] {record.getMessage()}</span>'
        self._text.appendHtml(line)

        # Auto-scroll to bottom
        self._text.verticalScrollBar().setValue(
            self._text.verticalScrollBar().maximum()
        )


class LogMainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._log_widget = LogWidget()
        self.setCentralWidget(self._log_widget)
        self.resize(700, 450)
        self.setWindowTitle("Catena Output Log")

        # Create handler and connect signal
        self._log_handler = QtLogHandler()
        self._log_handler.setLevel(logging.INFO)
        self._log_handler.log_record.connect(self._log_widget.append_record)

        # Attach to root logger (catches everything) or a named logger
        logging.getLogger().addHandler(self._log_handler)
        logging.getLogger().setLevel(logging.DEBUG)


window: Optional[LogMainWindow] = None


def init_log_window(parent: Optional[QtWidgets.QWidget] = None) -> None:
    global window
    if window is None:
        window = LogMainWindow(parent)


def show_log_window(parent: Optional[QtWidgets.QWidget] = None) -> None:
    """Show the singleton logger window."""
    init_log_window(parent)
    window.show()
