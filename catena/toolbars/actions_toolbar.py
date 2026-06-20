from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

from catena.nodes.graph_gui import GuiGraphView
from catena.toolbars.action_sub_bars.convert import ConvertToolbar
from catena.toolbars.action_sub_bars.file import CreateToolbar
from catena.toolbars.action_sub_bars.graph import GraphToolbar
from catena.toolbars.action_sub_bars.generator import GeneratorToolbar
from catena.toolbars.action_sub_bars.image import ImageToolbar
from catena.toolbars.action_sub_bars.math import MathToolbar
from catena.toolbars.action_sub_bars.switcher import ToolbarSwitcher
from catena.toolbars.action_sub_bars.transform import TransformToolbar


class EditorActionToolbar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: GuiGraphView) -> None:
        self.graph_view = graph_view
        super().__init__(
            "ActionsToolbar", default_button_resolution=[40, 40], parent=parent
        )

    def build(self) -> None:
        switcher = ToolbarSwitcher(self)

        switcher.add_toolbar("File", GraphToolbar(self, self.graph_view))
        switcher.add_toolbar("Convert", ConvertToolbar(self, self.graph_view))
        switcher.add_toolbar("Create", CreateToolbar(self, self.graph_view))
        switcher.add_toolbar("Generators", GeneratorToolbar(self, self.graph_view))
        switcher.add_toolbar("Image", ImageToolbar(self, self.graph_view))
        switcher.add_toolbar("Math", MathToolbar(self, self.graph_view))
        switcher.add_toolbar("Transform", TransformToolbar(self, self.graph_view))

        self.addWidget(switcher)
