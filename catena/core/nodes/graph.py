from PySide6TK import QtWidgets
from PySide6TK.Nodes import GraphView

from catena.core.nodes.comment import CatenaCommentBox
from catena.core.nodes.create.outro import OutroNode
from catena.core.nodes.create.read import ReadNode
from catena.core.nodes.create.start import StartNode
from catena.core.nodes.create.transition import TransitionNode
from catena.core.nodes.image.blur import BlurNode
from catena.core.nodes.image.color import ColorNode
from catena.core.nodes.image.contrast import ContrastNode
from catena.core.nodes.image.hsv import HSVNode
from catena.core.nodes.image.levels import LevelsNode
from catena.core.nodes.image.overlay import OverlayNode
from catena.core.nodes.image.sharpen import SharpenNode
from catena.core.nodes.image.threshold import ThresholdNode
from catena.core.nodes.math.add import AddNode
from catena.core.nodes.math.divide import DivideNode
from catena.core.nodes.math.multiply import MultiplyNode
from catena.core.nodes.math.subtract import SubtractNode
from catena.core.nodes.transform.flip import FlipNode
from catena.core.nodes.transform.offset import OffsetNode
from catena.core.nodes.transform.rotate import RotateNode


class CatenaGraphView(GraphView):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.comment_type = CatenaCommentBox
        self._register_nodes()

    def add_comment(
        self, x: float, y: float, label: str = "Comment"
    ) -> CatenaCommentBox:
        """
        Add a comment box to the scene at the given scene coordinates.

        Args:
            x (float): Scene x position.
            y (float): Scene y position.
            label (str): Initial comment label.
        Returns:
            CommentBox: The created comment box.
        """
        box = CatenaCommentBox(label)
        self._node_refs.append(box)
        self.scene.addItem(box)
        box.setPos(x, y)
        return box

    def _register_nodes(self) -> None:
        self._register_create_nodes()
        self._register_color_nodes()
        self._register_transform_nodes()
        self._register_math_nodes()

    def _register_create_nodes(self) -> None:
        self.register_node("Create", OutroNode)
        self.register_node("Create", ReadNode)
        self.register_node("Create", StartNode)
        self.register_node("Create", TransitionNode)

    def _register_color_nodes(self) -> None:
        self.register_node("Image", BlurNode)
        self.register_node("Image", ContrastNode)
        self.register_node("Image", ColorNode)
        self.register_node("Image", HSVNode)
        self.register_node("Image", LevelsNode)
        self.register_node("Image", OverlayNode)
        self.register_node("Image", SharpenNode)
        self.register_node("Image", ThresholdNode)

    def _register_transform_nodes(self) -> None:
        self.register_node("Transform", FlipNode)
        self.register_node("Transform", OffsetNode)
        self.register_node("Transform", RotateNode)

    def _register_math_nodes(self) -> None:
        self.register_node("Math", AddNode)
        self.register_node("Math", SubtractNode)
        self.register_node("Math", MultiplyNode)
        self.register_node("Math", DivideNode)
