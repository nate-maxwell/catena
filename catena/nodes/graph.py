import logging
import json

import broker
from PySide6 import QtGui
from PySide6TK import QtCore
from PySide6TK import QtWidgets
from PySide6TK.Nodes import GraphView
from PySide6TK.Nodes import Port
from PySide6TK.Nodes import PortType
from PySide6TK.Nodes import Wire
from core_utils import regex

from catena import namespace
from catena.nodes.comment import CatenaCommentBox
from catena.nodes.node import CatenaNode
from catena.nodes.registry import NodeRegistry

logger = logging.getLogger(__name__)


class GuiGraphView(GraphView):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.comment_type = CatenaCommentBox
        logger.info("Graph view initialized")

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
        self.graph_scene.addItem(box)
        box.setPos(x, y)
        return box

    def connect_ports_internal(self, source: Port, target: Port) -> Wire:
        wire = super().connect_ports_internal(source, target)

        self._invalidate_and_refresh_from_port(target)
        self._refresh_active_preview()

        return wire

    def destroy_wire(self, wire: Wire) -> None:
        target = wire.target

        super().destroy_wire(wire)

        if target is not None:
            self._invalidate_and_refresh_from_port(target)

        self._refresh_active_preview()

    @staticmethod
    def _invalidate_and_refresh_from_port(port: Port) -> None:
        node = port.parentItem()
        if not isinstance(node, CatenaNode):
            return

        node._invalidate_downstream()
        node._refresh_downstream_write_nodes()

    @staticmethod
    def _refresh_downstream_write_nodes(node: CatenaNode) -> None:
        if CatenaNode._preview_updates_suppressed():
            return

        visited: set[CatenaNode] = set()
        stack: list[CatenaNode] = [node]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)

            if hasattr(current, "WRITE_NODE_PREVIEW"):
                current._emit_preview_update()

            for output_port in current.output_ports():
                for wire in output_port.wires:
                    target_node = wire.target.parentItem()
                    if isinstance(target_node, CatenaNode):
                        stack.append(target_node)

    @staticmethod
    def _refresh_active_preview() -> None:
        if CatenaNode._preview_updates_suppressed():
            return

        node = CatenaNode.active_preview_node
        if node is not None:
            broker.emit(namespace.NODE_PREVIEW, image=node._preview_image())

    def copy_selected(self) -> None:
        """
        Copy selected nodes using Catena's registry-aware serializer.

        The base PySide6TK implementation only knows about the graph view's
        internal node registry, which Catena does not populate. That causes
        clipboard paste to drop custom nodes silently.
        """
        from catena.nodes import serialize as graph_serialize

        selected_nodes = [
            item
            for item in self.graph_scene.selectedItems()
            if isinstance(item, CatenaNode)
        ]
        if not selected_nodes:
            return

        data = graph_serialize.serialize_nodes(self, selected_nodes)
        QtGui.QGuiApplication.clipboard().setText(json.dumps(data))

    def paste_clipboard(self, x: float, y: float) -> None:
        """
        Paste nodes using Catena's registry-aware deserializer.

        This bypasses the base PySide6TK deserializer, which only consults the
        graph view's internal registry and therefore cannot resolve Catena's
        globally registered node classes.
        """
        from catena.nodes import serialize as graph_serialize

        text = QtGui.QGuiApplication.clipboard().text()
        if not text:
            return

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return

        if "nodes" not in data or not data["nodes"]:
            return

        graph_serialize.deserialize_nodes(self, data, offset=(x, y))

    def _on_context_menu(self, viewport_pos: QtCore.QPoint) -> None:
        """Overridden from parent to std_convert_nodes names from 'BevelNode' to 'Bevel'."""
        item = self.itemAt(viewport_pos)
        if item is not None:
            return

        scene_pos = self.mapToScene(viewport_pos)
        menu = QtWidgets.QMenu(self)

        comment_action = menu.addAction("Add Comment")
        comment_action.setData(("comment", scene_pos))
        menu.addSeparator()

        node_registry = NodeRegistry()

        for category, node_types in sorted(node_registry.to_dict().items()):
            submenu = menu.addMenu(category)
            for node_type in node_types:
                snake_case = regex.pascal_to_snake(node_type.__name__)
                name = snake_case.replace("_", " ").replace("node", "")
                entry = name.title()
                action = submenu.addAction(entry)
                action.setData(("node", node_type, scene_pos))

        chosen = menu.exec(self.viewport().mapToGlobal(viewport_pos))
        if chosen is None:
            return

        data = chosen.data()
        if data[0] == "comment":
            self.add_comment(data[1].x(), data[1].y())
        elif data[0] == "node":
            node = data[1]()
            self.add_node(node, data[2].x(), data[2].y())

    def _open_drop_menu(
        self,
        viewport_pos: QtCore.QPoint,
        scene_pos: QtCore.QPointF,
        drag_port: Port,
        reverse: bool,
    ) -> None:
        """
        Open the node-pick menu when a wire is dragged off a port.

        The base GraphView implementation uses ``self.node_registry``. Catena
        registers nodes globally, so we mirror the background context menu
        here to keep drop-spawn behavior consistent.
        """
        menu = QtWidgets.QMenu(self)

        for category, node_types in sorted(NodeRegistry().to_dict().items()):
            submenu = menu.addMenu(category)
            for node_type in node_types:
                snake_case = regex.pascal_to_snake(node_type.__name__)
                name = snake_case.replace("_", " ").replace("node", "")
                action = submenu.addAction(name.title())
                action.setData(node_type)

        chosen = menu.exec(self.viewport().mapToGlobal(viewport_pos))
        if chosen is None:
            return

        node_type = chosen.data()
        node = node_type()
        self.add_node(node, scene_pos.x(), scene_pos.y())

        candidate_ports = (
            node.input_ports()
            if drag_port.port_type == PortType.OUTPUT
            else node.output_ports()
        )
        if not candidate_ports:
            return

        target = candidate_ports[0]
        if reverse:
            source, target_final = target, drag_port
        else:
            source, target_final = drag_port, target

        if target_final.port_type == PortType.INPUT:
            for wire in list(target_final.wires):
                self.destroy_wire(wire)

        self.connect_ports(source, target_final)
