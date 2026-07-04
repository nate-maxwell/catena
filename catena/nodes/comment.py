from typing import Any

import broker
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6TK import QtWidgets
from PySide6TK.Nodes import CommentBox

from catena import namespace


class _MoveCommentCommand:
    def __init__(
        self,
        node: CommentBox,
        old_pos: QtCore.QPointF,
        new_pos: QtCore.QPointF,
    ) -> None:
        self._node = node
        self._old_pos = QtCore.QPointF(old_pos)
        self._new_pos = QtCore.QPointF(new_pos)

    def execute(self) -> None:
        self._node.setPos(self._new_pos)

    def undo(self) -> None:
        self._node.setPos(self._old_pos)


class CatenaCommentBox(CommentBox):

    def __init__(
        self,
        label: str = "Comment",
        width: int = 240,
        height: int = 160,
        parent: QtWidgets.QGraphicsItem | None = None,
    ) -> None:
        self._allow_click_selection = False
        self._move_origin: QtCore.QPointF | None = None
        super().__init__(label, width, height, parent)

    def _select_from_click(self) -> None:
        self._allow_click_selection = True
        try:
            self.setSelected(True)
        finally:
            self._allow_click_selection = False

        broker.emit(namespace.NODE_SELECTED, node=self)

    def _graph_commands(self) -> object | None:
        scene = self.scene()
        if scene is None:
            return None
        views = scene.views()
        if not views:
            return None
        return getattr(views[0], "commands", None)

    def _push_move_command(self) -> None:
        if self._move_origin is None:
            return

        new_pos = self.pos()
        if new_pos == self._move_origin:
            return

        commands = self._graph_commands()
        if commands is None or not hasattr(commands, "push"):
            return

        commands.push(_MoveCommentCommand(self, self._move_origin, new_pos))

    def shape(self) -> QtGui.QPainterPath:
        path = QtGui.QPainterPath()
        path.addRoundedRect(
            QtCore.QRectF(0, 0, self._box_width, self._box_height),
            self._CORNER_RADIUS,
            self._CORNER_RADIUS,
        )
        return path

    def itemChange(
        self,
        change: QtWidgets.QGraphicsItem.GraphicsItemChange,
        value: object,
    ) -> object:
        if (
            change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSelectedChange
            and value
            and not self._allow_click_selection
        ):
            return self.isSelected()
        return super().itemChange(change, value)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        self._move_origin = self.pos()
        if self._corner_at(event.pos()) != self._CORNER_NONE:
            super().mousePressEvent(event)
            return

        self._select_from_click()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Emit a double-click event to open the properties panel.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        self._select_from_click()
        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        try:
            super().mouseReleaseEvent(event)
        finally:
            self._push_move_command()
            self._move_origin = None

    def set_field_value(self, name: str, value: Any) -> None:
        super().set_field_value(name, value)
        self.update()
