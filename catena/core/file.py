from pathlib import Path
from typing import Optional

from PySide6 import QtWidgets

from catena.core import appdata


def open_file_dialog(
    parent: Optional[QtWidgets.QWidget] = None,
    title: str = "Open File",
    directory: str = "",
    file_filter: str = f"Catena Graph (*{appdata.CATENA_FILE_SUFFIX});;All Files (*)",
) -> Optional[Path]:
    """
    Show a file open dialog and return the selected path.

    Args:
        parent (QtWidgets.QWidget | None): Optional parent widget.
        title (str): The dialog title.
        directory (str): The initial directory to show.
        file_filter (str): The file type filter string.
    Returns:
        Path | None: The selected file path, or None if cancelled.
    """
    filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
        parent, title, directory, file_filter
    )
    if not filepath:
        return None
    return Path(filepath)


def save_file_dialog(
    parent: Optional[QtWidgets.QWidget] = None,
    title: str = "Save File",
    directory: str = "",
    file_filter: str = f"Catena Graph (*{appdata.CATENA_FILE_SUFFIX});;All Files (*)",
) -> Optional[Path]:
    """
    Show a file save dialog and return the selected path.

    Args:
        parent (QtWidgets.QWidget | None): Optional parent widget.
        title (str): The dialog title.
        directory (str): The initial directory to show.
        file_filter (str): The file type filter string.
    Returns:
        Path | None: The selected file path, or None if cancelled.
    """
    filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
        parent, title, directory, file_filter
    )
    if not filepath:
        return None
    return Path(filepath)
