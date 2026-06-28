from __future__ import annotations

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class MinimapWidget(QtWidgets.QWidget):
    """
    A minimap overlay that renders a scaled-down birds-eye view of all nodes
    in a QGraphicsScene and shows the current viewport position as a
    translucent rectangle. Clicking or dragging pans the graph view.
    """

    _PADDING = 12
    _WIDTH = 200
    _HEIGHT = 140
    _BG_COLOR = QtGui.QColor(20, 20, 20, 200)
    _BORDER_COLOR = QtGui.QColor(60, 60, 60, 255)
    _NODE_COLOR = QtGui.QColor(90, 90, 90, 220)
    _VIEW_COLOR = QtGui.QColor(255, 255, 255, 40)
    _VIEW_BORDER = QtGui.QColor(200, 200, 200, 160)

    def __init__(
        self, graph_view: QtWidgets.QGraphicsView, parent: QtWidgets.QWidget
    ) -> None:
        super().__init__(parent)
        self._graph_view = graph_view
        self._dragging = False

        self.setFixedSize(self._WIDTH, self._HEIGHT)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setCursor(QtCore.Qt.CursorShape.CrossCursor)

        # Rerender whenever the scene or viewport changes
        self._graph_view.graph_scene.changed.connect(self._on_scene_changed)
        self._graph_view.horizontalScrollBar().valueChanged.connect(self.update)
        self._graph_view.verticalScrollBar().valueChanged.connect(self.update)
        self._graph_view.installEventFilter(self)

        self._position_in_corner()

    # ── layout ───────────────────────────────────────────────────────────────

    def _position_in_corner(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return
        x = parent.width() - self._WIDTH - self._PADDING
        y = parent.height() - self._HEIGHT - self._PADDING
        self.move(max(self._PADDING, x), max(self._PADDING, y))

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self._position_in_corner()

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if obj is self._graph_view and event.type() in (
            QtCore.QEvent.Type.Resize,
            QtCore.QEvent.Type.Show,
        ):
            self._position_in_corner()
            self.raise_()
        return super().eventFilter(obj, event)

    # ── coordinate helpers ───────────────────────────────────────────────────

    def _scene_rect(self) -> QtCore.QRectF:
        """Bounding rect of all items in the scene, falling back to sceneRect."""
        items = self._graph_view.graph_scene.items()
        if not items:
            return self._graph_view.graph_scene.sceneRect()
        rects = [i.mapToScene(i.boundingRect()).boundingRect() for i in items]
        result = rects[0]
        for r in rects[1:]:
            result = result.united(r)
        # Add a small margin
        result.adjust(-40, -40, 40, 40)
        return result

    def _scene_to_mini(self, scene_rect: QtCore.QRectF) -> QtCore.QTransform:
        """Transform from scene coordinates to minimap widget coordinates."""
        inner = QtCore.QRectF(4, 4, self._WIDTH - 8, self._HEIGHT - 8)
        sx = inner.width() / max(scene_rect.width(), 1)
        sy = inner.height() / max(scene_rect.height(), 1)
        scale = min(sx, sy)
        # Center the scaled scene rect inside the inner area
        scaled_w = scene_rect.width() * scale
        scaled_h = scene_rect.height() * scale
        ox = inner.x() + (inner.width() - scaled_w) / 2
        oy = inner.y() + (inner.height() - scaled_h) / 2
        t = QtGui.QTransform()
        t.translate(ox - scene_rect.x() * scale, oy - scene_rect.y() * scale)
        t.scale(scale, scale)
        return t

    def _mini_to_scene(
        self, scene_rect: QtCore.QRectF, mini_pos: QtCore.QPointF
    ) -> QtCore.QPointF:
        t = self._scene_to_mini(scene_rect)
        inv, ok = t.inverted()
        if not ok:
            return QtCore.QPointF()
        return inv.map(mini_pos)

    # ── painting ─────────────────────────────────────────────────────────────

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # Background
        painter.setPen(QtGui.QPen(self._BORDER_COLOR, 1))
        painter.setBrush(self._BG_COLOR)
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 6, 6)

        scene_rect = self._scene_rect()
        if scene_rect.isEmpty():
            return

        t = self._scene_to_mini(scene_rect)
        painter.setTransform(t)

        # Draw each node as a filled rect
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(self._NODE_COLOR)
        for item in self._graph_view.graph_scene.items():
            br = item.mapToScene(item.boundingRect()).boundingRect()
            painter.drawRect(br)

        # Draw current viewport rect
        viewport_scene = self._graph_view.mapToScene(
            self._graph_view.viewport().rect()
        ).boundingRect()
        painter.setPen(QtGui.QPen(self._VIEW_BORDER, 2 / t.m11()))
        painter.setBrush(self._VIEW_COLOR)
        painter.drawRect(viewport_scene)

        painter.resetTransform()

    # ── interaction ──────────────────────────────────────────────────────────

    def _pan_to(self, mini_pos: QtCore.QPointF) -> None:
        scene_rect = self._scene_rect()
        scene_pos = self._mini_to_scene(scene_rect, mini_pos)
        self._graph_view.centerOn(scene_pos)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._dragging = True
            self._pan_to(event.position())

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._dragging:
            self._pan_to(event.position())

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self._dragging = False

    # ── scene change ─────────────────────────────────────────────────────────

    def _on_scene_changed(self, *_: object) -> None:
        self.update()
