from PySide6TK import QtWidgets


class ToolbarSwitcher(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """
        A Maya-style shelf — a tab bar that switches between toolbars.

        Args:
            parent (QtWidgets.QWidget | None): Optional parent widget.
        """

        super().__init__(parent)

        self._layout_main = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout_main)
        self._layout_main.setContentsMargins(0, 0, 0, 0)
        self._layout_main.setSpacing(0)

        self._stack = QtWidgets.QStackedWidget(self)
        self._tab_bar = QtWidgets.QTabBar(self)
        self._tab_bar.currentChanged.connect(self._stack.setCurrentIndex)
        self._tab_bar.setExpanding(False)

        self._layout_main.addWidget(self._tab_bar)
        self._layout_main.addWidget(self._stack)

    def add_toolbar(self, label: str, toolbar: QtWidgets.QToolBar) -> None:
        """
        Add a toolbar tab.

        Args:
            label (str): The text to fill the tab that switches to the toolbar.
            toolbar (QtWidgets.QToolBar): The toolbar to switch to.
        """
        toolbar.setMovable(False)
        self._tab_bar.addTab(label)
        self._stack.addWidget(toolbar)
