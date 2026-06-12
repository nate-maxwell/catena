import broker
from PySide6 import QtWidgets
from PySide6TK.Nodes import BaseNode

from catena.core import namespace


class CatenaNode(BaseNode):
    def __init__(self, title: str, width: int, body_height: int) -> None:
        super().__init__(title, width, body_height)

    def mouseDoubleClickEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Called when the node is double-clicked.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        broker.emit(namespace.NODE_DOUBLE_CLICK, node=self)
        super().mouseDoubleClickEvent(event)
