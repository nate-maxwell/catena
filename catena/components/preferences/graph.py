from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

from catena.components.preferences.topic_menu import PreferenceTopicMenu
from catena.core.prefs import category_data


class GraphPreferencesMenu(PreferenceTopicMenu):

    def __init__(self) -> None:
        super().__init__("Graph")

        self.topic_prefs = self.prefs.node_graph_preferences

        self.wire_style = QtWrappers.LabeledComboBox(
            "Wire Style", category_data.WIRE_STYLES, False
        )
        self.wire_style.set_current_text(self.topic_prefs.wire_style)
        self.add_widget(self.wire_style)

        self.glayout_colors = QtWrappers.GridLayout()
        self.add_layout(self.glayout_colors)

        self.glayout_colors.add_to_new_row(QtWidgets.QLabel("Small Grid Color"))
        self.small_grid_color = QtWrappers.ColorButton(
            self.topic_prefs.small_grid_color
        )
        self.glayout_colors.add_to_last_row(self.small_grid_color)

        self.glayout_colors.add_to_new_row(QtWidgets.QLabel("Large Grid Color"))
        self.large_grid_color = QtWrappers.ColorButton(
            self.topic_prefs.large_grid_color
        )
        self.glayout_colors.add_to_last_row(self.large_grid_color)

        self.zoom_step = QtWrappers.LabeledSpinBox(
            "Zoom Step", True, self.topic_prefs.zoom_step
        )
        self.add_widget(self.zoom_step)

        self.add_stretch()

    def sync_settings(self) -> None:
        self.topic_prefs.wire_style = self.wire_style.current_text()
        self.topic_prefs.small_grid_color = self.small_grid_color.color().name()
        self.topic_prefs.large_grid_color = self.large_grid_color.color().name()
        self.topic_prefs.zoom_step = self.zoom_step.value()
