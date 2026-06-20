from typing import Optional

from PySide6TK import QtCore
from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

from catena.components.preferences.general import GeneralPreferencesMenu
from catena.components.preferences.graph import GraphPreferencesMenu
from catena.components.preferences.layout import LayoutPreferencesMenu
from catena.core.prefs import preferences


class PreferencesMenu(QtWrappers.MainWindow):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__("Preferences", parent=parent)
        self.settings_before = preferences.Preferences().to_dict()

        self._create_widgets()
        self._create_layouts()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        # Individual preference widgets
        self.stack_topics = QtWidgets.QStackedWidget()
        self.general_preferences = GeneralPreferencesMenu()
        self.graph_preferences = GraphPreferencesMenu()
        self.layout_preferences = LayoutPreferencesMenu()

        # Topic selector
        self.sa_topic_buttons = QtWrappers.ScrollArea()
        self.sa_topic_buttons.setFixedWidth(200)
        self.btn_general_preferences = QtWidgets.QPushButton("General")
        self.btn_graph_preferences = QtWidgets.QPushButton("Graph")
        self.btn_layout_preferences = QtWidgets.QPushButton("Layout")

        # Ok, Cancel, Apply action buttons
        self.hlayout_actions = QtWidgets.QHBoxLayout()
        self.btn_ok = QtWidgets.QPushButton("Ok")
        self.btn_ok.setFixedWidth(100)
        self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_cancel.setFixedWidth(100)
        self.btn_apply = QtWidgets.QPushButton("Apply")
        self.btn_apply.setFixedWidth(100)

    def _create_layouts(self) -> None:
        # Topics
        self.stack_topics.addWidget(self.general_preferences)
        self.stack_topics.addWidget(self.graph_preferences)
        self.stack_topics.addWidget(self.layout_preferences)
        self.stack_topics.addWidget(QtWrappers.VerticalLine())
        self.stack_topics.setCurrentIndex(0)

        # Menu selection buttons
        self.sa_topic_buttons.add_widget(self.btn_general_preferences)
        self.sa_topic_buttons.add_widget(self.btn_graph_preferences)
        self.sa_topic_buttons.add_widget(self.btn_layout_preferences)
        self.sa_topic_buttons.add_stretch()

        # Splitter
        self.splitter.addWidget(self.sa_topic_buttons)
        self.splitter.addWidget(self.stack_topics)

        # Action buttons
        self.hlayout_actions.addStretch()
        self.hlayout_actions.addWidget(self.btn_ok)
        self.hlayout_actions.addWidget(self.btn_cancel)
        self.hlayout_actions.addWidget(self.btn_apply)

        # Main
        self.setCentralWidget(self.widget_main)
        self.widget_main.setLayout(self.layout_main)
        self.layout_main.addWidget(self.splitter)
        self.layout_main.addLayout(self.hlayout_actions)

    def _create_connections(self) -> None:
        # Action buttons
        self.btn_ok.clicked.connect(self.ok)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_apply.clicked.connect(self.apply)

        # Menu selection buttons
        self.btn_general_preferences.clicked.connect(
            lambda: self.stack_topics.setCurrentWidget(self.general_preferences)
        )
        self.btn_graph_preferences.clicked.connect(
            lambda: self.stack_topics.setCurrentWidget(self.graph_preferences)
        )
        self.btn_layout_preferences.clicked.connect(
            lambda: self.stack_topics.setCurrentWidget(self.layout_preferences)
        )

    def _sync_settings(self) -> None:
        self.general_preferences.sync_settings()
        self.graph_preferences.sync_settings()
        self.layout_preferences.sync_settings()

    def ok(self) -> None:
        self._sync_settings()
        preferences.Preferences().save()

    def apply(self) -> None:
        self._sync_settings()
        preferences.Preferences().save()

        global window
        window = None
        self.close()
        self.deleteLater()

    def cancel(self) -> None:
        global window
        window = None

        prefs = preferences.Preferences()
        prefs.from_dict(self.settings_before)
        self.close()
        self.deleteLater()


window: Optional[PreferencesMenu] = None


def show_preferences_widget(parent: Optional[QtWidgets.QWidget] = None) -> None:
    """Show the singleton preferences widget."""
    global window
    if window is None:
        window = PreferencesMenu(parent)

    window.show()
