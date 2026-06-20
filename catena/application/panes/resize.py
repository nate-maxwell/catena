from PySide6TK import QtCore
from PySide6TK import QtWidgets


def split_vertical(
    parent: QtWidgets.QMainWindow,
    first: QtWidgets.QDockWidget,
    second: QtWidgets.QDockWidget,
    ratio: float,
) -> None:
    """
    Resize two vertically split dock widgets by ratio after layout.

    Args:
        parent (QtWidgets.QMainWindow): The parent window.
        first (QtWidgets.QDockWidget): The top dock widget.
        second (QtWidgets.QDockWidget): The bottom dock widget.
        ratio (float): Fraction of total height given to first, e.g. 0.5.
    Returns:
        None: No return value.
    """

    def _resize() -> None:
        h1, h2 = first.height(), second.height()
        total = h1 + h2
        sizes = [int(total * ratio), int(total * (1.0 - ratio))]
        parent.resizeDocks([first, second], sizes, QtCore.Qt.Orientation.Vertical)

    QtCore.QTimer.singleShot(50, _resize)


def split_horizontal(
    parent: QtWidgets.QMainWindow,
    first: QtWidgets.QDockWidget,
    second: QtWidgets.QDockWidget,
    ratio: float,
) -> None:
    """
    Resize two horizontally split dock widgets by ratio after layout.

    Args:
        parent (QtWidgets.QMainWindow): The parent window.
        first (QtWidgets.QDockWidget): The left dock widget.
        second (QtWidgets.QDockWidget): The right dock widget.
        ratio (float): Fraction of total width given to first, e.g. 0.7.
    Returns:
        None: No return value.
    """

    def _resize() -> None:
        h1, h2 = first.height(), second.height()
        total = h1 + h2
        sizes = [int(total * ratio), int(total * (1.0 - ratio))]
        parent.resizeDocks([first, second], sizes, QtCore.Qt.Orientation.Horizontal)

    QtCore.QTimer.singleShot(50, _resize)
