from typing import Optional

from PySide6TK import QtWidgets
from PySide6TK.Nodes import GraphView

from catena.core.nodes.comment import CatenaCommentBox
from catena.core.nodes.outro import OutroNode
from catena.core.nodes.panel import PanelNode
from catena.core.nodes.start import StartNode
from catena.core.nodes.transition import TransitionNode


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
        self.register_node("Main", StartNode)
        self.register_node("Main", PanelNode)
        self.register_node("Main", TransitionNode)
        self.register_node("Main", OutroNode)
