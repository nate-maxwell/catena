from PySide6TK import QtWrappers

from catena.components.preferences.topic_menu import PreferenceTopicMenu
from catena.core.prefs import category_data


class LayoutPreferencesMenu(PreferenceTopicMenu):

    def __init__(self) -> None:
        super().__init__("General")

        self.topic_prefs = self.prefs.layout_preferences

        self.selected_layout = QtWrappers.LabeledComboBox(
            "Layout", category_data.LAYOUTS
        )
        self.selected_layout.set_current_text(self.topic_prefs.selected_layout)
        self.add_widget(self.selected_layout)

        self.add_stretch()

    def sync_settings(self) -> None:
        self.topic_prefs.selected_layout = self.selected_layout.current_text()
