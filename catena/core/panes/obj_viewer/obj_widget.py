"""
A thin wrapper for the ObjViewer widget that adds a combo box for switching
which model is loaded.
"""

from pathlib import Path

from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

from catena.core import resources
from catena.core.panes.obj_viewer.obj_viewer import ObjViewer

_models: dict[str, Path] = {
    "Cylinder": resources.GEO_CYLINDER,
    "Cube": resources.GEO_CUBE,
    "Plane": resources.GEO_PLANE,
    "Shader Ball": resources.GEO_SHADER_BALL,
}


class ObjectViewerWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._create_widgets()
        self._create_layouts()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.layout_main = QtWidgets.QVBoxLayout()
        self.obj_view = ObjViewer(self)

        self.cmb_model = QtWrappers.LabeledComboBox(
            "Preview Model", ["Cylinder", "Cube", "Plane", "Shader Ball"], False
        )
        self.cmb_model.set_current_text("Cube")

    def _create_layouts(self) -> None:
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.cmb_model)
        self.layout_main.addWidget(self.obj_view)

    def _create_connections(self) -> None:
        self.cmb_model.cmb_box.currentIndexChanged.connect(self._refresh)

    def _refresh(self) -> None:
        selected = self.cmb_model.current_text()
        new_model = _models[selected]
        self.obj_view.set_model(new_model)
