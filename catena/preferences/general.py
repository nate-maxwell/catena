from PySide6TK import QtWrappers

from catena.preferences.topic_menu import PreferenceTopicMenu


class GeneralPreferencesMenu(PreferenceTopicMenu):

    def __init__(self) -> None:
        super().__init__("General")

        self.topic_prefs = self.prefs.general_preferences

        self.texture_resolution = QtWrappers.LabeledSpinBox("Texture Resolution")
        self.texture_resolution.set_value(self.topic_prefs.texture_resolution)
        self.add_widget(self.texture_resolution)

        self.add_stretch()

    def sync_settings(self) -> None:
        self.topic_prefs.texture_resolution = self.texture_resolution.value()
