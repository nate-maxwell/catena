"""
A UI interface to read and update Solaire's underlying application data, namely
its preferences.

As the system works without the user interacting with preference data, this is
not categorized as a "core" feature.
"""

from PySide6TK import QtWrappers

from catena.core.prefs import preferences

ENABLED = "Enabled"
DISABLED = "Disabled"


class PreferenceTopicMenu(QtWrappers.GroupBox):

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name
        self.prefs = preferences.Preferences()
        self.scroll_area = QtWrappers.ScrollArea()
        self.add_widget(self.scroll_area)
        self.add_widget = self.scroll_area.add_widget
        self.add_stretch = self.scroll_area.add_stretch
        self.add_layout = self.scroll_area.add_layout

    def sync_settings(self) -> None:
        raise NotImplementedError
