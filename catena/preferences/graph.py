from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

from catena.preferences import category_data
from catena.preferences.topic_menu import PreferenceTopicMenu


class GraphPreferencesMenu(PreferenceTopicMenu):

    def __init__(self) -> None:
        super().__init__("Graph")

        self.topic_prefs = self.prefs["node_graph_preferences"]

        # -----Wire Style-----
        self.wire_style = QtWrappers.LabeledComboBox(
            "Wire Style", category_data.WIRE_STYLES, False
        )
        self.wire_style.set_current_text(self.topic_prefs.wire_style)
        self.add_widget(self.wire_style)

        # -----Grid Values-----
        self.glayout_grid = QtWrappers.GridLayout()
        self.add_layout(self.glayout_grid)

        self.glayout_grid.add_to_new_row(QtWidgets.QLabel("Small Grid Color"))
        self.small_grid_color = QtWrappers.ColorButton(
            self.topic_prefs.color_grid_small
        )
        self.glayout_grid.add_to_last_row(self.small_grid_color)

        self.glayout_grid.add_to_new_row(QtWidgets.QLabel("Large Grid Color"))
        self.large_grid_color = QtWrappers.ColorButton(
            self.topic_prefs.color_grid_large
        )
        self.glayout_grid.add_to_last_row(self.large_grid_color)

        self.glayout_grid.add_to_new_row(QtWidgets.QLabel("Grid Background Color"))
        self.bg_grid_color = QtWrappers.ColorButton(self.topic_prefs.color_grid_bg)
        self.glayout_grid.add_to_last_row(self.bg_grid_color)

        self.grid_size_small = QtWrappers.LabeledSpinBox("Grid Size Small", True)
        self.grid_size_small.set_value(self.topic_prefs.grid_size_small)
        self.add_widget(self.grid_size_small)

        self.grid_size_large = QtWrappers.LabeledSpinBox("Grid Size Large", True)
        self.grid_size_large.set_value(self.topic_prefs.grid_size_large)
        self.add_widget(self.grid_size_large)

        # -----Zoom-----
        self.zoom_step = QtWrappers.LabeledSpinBox("Zoom Step", True)
        self.zoom_step.set_value(self.topic_prefs.zoom_step)
        self.add_widget(self.zoom_step)

        self.zoom_min = QtWrappers.LabeledSpinBox("Zoom Min", True)
        self.zoom_min.set_value(self.topic_prefs.zoom_min)
        self.add_widget(self.zoom_min)

        self.zoom_max = QtWrappers.LabeledSpinBox("Zoom Max", True)
        self.zoom_max.set_value(self.topic_prefs.zoom_max)
        self.add_widget(self.zoom_max)

        self.add_stretch()

    def sync_settings(self) -> None:
        self.topic_prefs.wire_style = self.wire_style.current_text()

        self.topic_prefs.color_grid_bg = self.bg_grid_color.color().name()
        self.topic_prefs.color_grid_small = self.small_grid_color.color().name()
        self.topic_prefs.color_grid_large = self.large_grid_color.color().name()

        self.topic_prefs.grid_size_small = self.grid_size_small.value()
        self.topic_prefs.grid_size_large = self.grid_size_large.value()

        self.topic_prefs.zoom_step = self.zoom_step.value()
        self.topic_prefs.zoom_min = self.zoom_min.value()
        self.topic_prefs.zoom_max = self.zoom_max.value()
