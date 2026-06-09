from PySide6 import QtCore
from PySide6 import QtWidgets


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
    QtCore.QTimer.singleShot(
        0,
        lambda: parent.resizeDocks(
            [first, second],
            [int(parent.height() * ratio), int(parent.height() * (1.0 - ratio))],
            QtCore.Qt.Orientation.Vertical,
        ),
    )


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
    QtCore.QTimer.singleShot(
        0,
        lambda: parent.resizeDocks(
            [first, second],
            [int(parent.width() * ratio), int(parent.width() * (1.0 - ratio))],
            QtCore.Qt.Orientation.Horizontal,
        ),
    )
