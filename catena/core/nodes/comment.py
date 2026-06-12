from typing import Any

import broker
from PySide6TK import QtWidgets
from PySide6TK.Nodes import CommentBox

from catena.core import namespace


class CatenaCommentBox(CommentBox):

    def __init__(
        self,
        label: str = "Comment",
        width: int = 240,
        height: int = 160,
        parent: QtWidgets.QGraphicsItem | None = None,
    ) -> None:
        super().__init__(label, width, height, parent)

    def mouseDoubleClickEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Emit a double-click event to open the properties panel.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        broker.emit(namespace.NODE_DOUBLE_CLICK, node=self)
        super().mouseDoubleClickEvent(event)

    def set_field_value(self, name: str, value: Any) -> None:
        super().set_field_value(name, value)
        self.update()
