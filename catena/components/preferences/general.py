from PySide6TK import QtWrappers

from catena.components.preferences.topic_menu import PreferenceTopicMenu


class GeneralPreferencesMenu(PreferenceTopicMenu):

    def __init__(self) -> None:
        super().__init__("General")

        self.topic_prefs = self.prefs.general_preferences

        self.auto_save_interval = QtWrappers.LabeledSpinBox("Auto Save Interval")
        self.auto_save_interval.set_value(self.topic_prefs.auto_save_interval)
        self.add_widget(self.auto_save_interval)

        self.add_stretch()

    def sync_settings(self) -> None:
        self.topic_prefs.auto_save_interval = self.auto_save_interval.value()
