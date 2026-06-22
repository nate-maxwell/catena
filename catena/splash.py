import logging

from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets

logger = logging.getLogger(__name__)


class CatenaSplashScreen(QtWidgets.QSplashScreen):

    def __init__(self, pixmap: QtGui.QPixmap) -> None:
        super().__init__(pixmap, QtCore.Qt.WindowType.WindowStaysOnTopHint)
        logger.info("Splash screen initialized")
        self._left_text = ""
        self._right_text = ""

    def set_texts(self, left: str, right: str) -> None:
        self._left_text = left
        self._right_text = right
        self.repaint()

    def drawContents(self, painter: QtGui.QPainter) -> None:
        painter.setPen(QtGui.QColor(QtCore.Qt.GlobalColor.white))
        rect = self.rect().adjusted(10, 0, -10, -10)
        painter.drawText(
            rect,
            QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft,
            self._left_text,
        )
        painter.drawText(
            rect,
            QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignRight,
            self._right_text,
        )
