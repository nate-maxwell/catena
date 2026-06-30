from pathlib import Path

from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

from catena.plugins import discover
from catena.plugins import plugin_record


class PluginEntry(QtWrappers.GroupBox):
    """
    Single row entry displaying the data for a single plugin.
    Data includes things such as plugin name, author, version, description...

    Contains a checkbox to enable and disable the plugin.
    """

    def __init__(
        self, parent: "PluginMenuDialog", metadata: discover.PluginDescriptor
    ) -> None:
        self.parent = parent
        self.path = metadata.path
        name = metadata.name
        description = metadata.description
        version = metadata.version
        author = metadata.author
        enabled = metadata.enabled
        super().__init__(name)

        layout_main = QtWidgets.QHBoxLayout()
        layout_main.setContentsMargins(0, 0, 0, 0)
        layout_main.setSpacing(12)

        scale = 256 - 64

        icon_path = self._find_icon_path()
        if icon_path is not None:
            icon_label = QtWidgets.QLabel()
            icon_pixmap = QtGui.QPixmap(icon_path.as_posix())
            if not icon_pixmap.isNull():
                icon_label.setPixmap(
                    icon_pixmap.scaled(
                        scale,
                        scale,
                        QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                        QtCore.Qt.TransformationMode.SmoothTransformation,
                    )
                )
                icon_label.setFixedSize(scale, scale)
                icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                layout_main.addWidget(icon_label)

        grid = QtWrappers.GridLayout()
        layout_main.addLayout(grid)
        grid.add_to_new_row(QtWidgets.QLabel("Description:"))
        grid.add_to_last_row(QtWidgets.QLabel(description))
        grid.add_to_new_row(QtWidgets.QLabel("Version:"))
        grid.add_to_last_row(QtWidgets.QLabel(version))
        grid.add_to_new_row(QtWidgets.QLabel("Author:"))
        grid.add_to_last_row(QtWidgets.QLabel(author))

        layout_main.addStretch()

        self.add_layout(layout_main)

        self.check_box = QtWidgets.QCheckBox("Enabled")
        self.check_box.setChecked(enabled)
        self.add_widget(self.check_box)

        self.check_box.toggled.connect(self._update_parent)

    def _find_icon_path(self) -> Path | None:
        for candidate in self.path.rglob("icon.png"):
            if candidate.is_file():
                return candidate
        return None

    def _update_parent(self) -> None:
        self.parent.set_plugin_enabled(self.check_box.isChecked(), self.path)


class PluginMenuDialog(QtWidgets.QDialog):
    """
    A dialog that lists all discovered plugins and allows the user to
    enable or disable each one.
    """

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Plugin Manager")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self._plugin_data: list[discover.PluginDescriptor] = []
        self._initial_states: dict[Path, bool] = {}
        self._changed: bool = False
        self._build()

    def _build(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        scroll_box = QtWrappers.ScrollArea()
        layout.addWidget(scroll_box)

        plugins = discover.discover_plugins()

        if not plugins:
            label = QtWidgets.QLabel(
                "No plugins found.\n\n"
                "Set CATENA_PLUGIN_PATHS to a directory containing "
                "plugin folders with a plugin.json file.",
                self,
            )
            label.setWordWrap(True)
            layout.addWidget(label)
        else:
            for metadata in plugins:
                checkbox = PluginEntry(self, metadata)
                self._plugin_data.append(metadata)
                self._initial_states[metadata.path] = metadata.enabled
                scroll_box.add_widget(checkbox)

        scroll_box.add_stretch()

        close_btn = QtWidgets.QPushButton("Close", self)
        close_btn.clicked.connect(self.accept)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def set_plugin_enabled(self, checked: bool, p: Path) -> None:
        # This can almost certainly be better - Probably some hashable lookup
        for i in self._plugin_data:
            if i.path == p:
                i.enabled = checked
                self._changed = self._initial_states.get(p) != checked
                return

    def accept(self) -> None:
        record = plugin_record.PluginRecordData()

        for descriptor in self._plugin_data:
            record.set_disabled(descriptor.path, not descriptor.enabled)

        record.save()

        if self._changed:
            QtWidgets.QMessageBox.information(
                self,
                "Restart Required",
                "Plugin changes will take effect after restarting Catena.",
            )

        super().accept()


def show_plugins_menu() -> None:
    menu = PluginMenuDialog()
    menu.exec()
