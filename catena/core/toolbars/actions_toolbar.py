from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

from catena.core.nodes.graph import CatenaGraphView
from catena.core.toolbars.action_sub_bars.switcher import ToolbarSwitcher
from catena.core.toolbars.action_sub_bars.file import FileToolbar
from catena.core.toolbars.action_sub_bars.create import CreateToolbar
from catena.core.toolbars.action_sub_bars.image import ImageToolbar
from catena.core.toolbars.action_sub_bars.transform import TransformToolbar
from catena.core.toolbars.action_sub_bars.math import MathToolbar
from catena.core.toolbars.action_sub_bars.generator import GeneratorToolbar


class EditorActionToolbar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: CatenaGraphView) -> None:
        self.graph_view = graph_view
        super().__init__(
            "Example Toolbar", default_button_resolution=[40, 40], parent=parent
        )

    def build(self) -> None:
        switcher = ToolbarSwitcher(self)

        switcher.add_toolbar("File", FileToolbar(self, self.graph_view))
        switcher.add_toolbar("Create", CreateToolbar(self, self.graph_view))
        switcher.add_toolbar("Generators", GeneratorToolbar(self, self.graph_view))
        switcher.add_toolbar("Image", ImageToolbar(self, self.graph_view))
        switcher.add_toolbar("Math", MathToolbar(self, self.graph_view))
        switcher.add_toolbar("Transform", TransformToolbar(self, self.graph_view))

        self.addWidget(switcher)
