from contextlib import contextmanager
import logging
from typing import Any
from typing import Optional

import broker
import numpy
from PySide6 import QtWidgets
from PySide6TK.Nodes import BaseNode
from PySide6TK.Nodes import Port
from PySide6TK.Nodes import PortType
from PySide6TK.Nodes import FieldType

from catena import namespace
from catena.nodes.data import PortDataType
from catena.nodes.data import FIELD_PORT_DATA_TYPES
from catena.nodes.data import DATA_TYPE_COLORS

logger = logging.getLogger(__name__)


class CatenaNode(BaseNode):

    active_preview_node: Optional["CatenaNode"] = None
    _preview_update_depth: int = 0

    def __init__(self, title: str, width: int = 160, body_height: int = 40) -> None:
        self._is_active_preview: bool = False
        self._promoted_fields: dict[str, Port] = {}

        self._cached_value: Any = None
        """The last evaluated value. Updates when field values change."""

        super().__init__(title, width, body_height)

        logger.info(f"{title} node created")

    @classmethod
    @contextmanager
    def suspend_preview_updates(cls):
        """Temporarily suppress preview broadcasts while rebuilding graphs."""
        cls._preview_update_depth += 1
        try:
            yield
        finally:
            cls._preview_update_depth -= 1

    @classmethod
    def _preview_updates_suppressed(cls) -> bool:
        return cls._preview_update_depth > 0

    def add_port(
        self, port_type: str, name: str, data_type: str = PortDataType.VECTOR4
    ) -> Port:
        """
        Create and position a port on this node.

        Input ports are placed on the left edge, output ports on the right.
        Ports are stacked top-to-bottom in the order they are added.

        Args:
            port_type (str): Either ``PortType.INPUT`` or ``PortType.OUTPUT``.
            name (str): Display name for the port.
            data_type (str): The data type of the port.
        Returns:
            Port: The created port.
        """
        input_count = sum(1 for p in self._ports if p.port_type == PortType.INPUT)
        output_count = sum(1 for p in self._ports if p.port_type == PortType.OUTPUT)

        port = Port(port_type, name, data_type, self)
        port.set_color(DATA_TYPE_COLORS[data_type])
        y = (
            self._HEADER_HEIGHT
            + self._PORT_MARGIN
            + (input_count if port_type == PortType.INPUT else output_count)
            * self._PORT_SPACING
        )

        x = 0 if port_type == PortType.INPUT else self.width
        port.setPos(x, y)
        self._ports.append(port)

        self._resize_to_fit_ports()
        self.update()

        return port

    def promote_field(self, name: str) -> None:
        """
        Promote a field to an input port, allowing it to receive upstream
        image data instead of a fixed field value.

        When the port is connected, the mean of the upstream image is used
        as the field value. When disconnected, the field value is used as
        normal.

        Args:
            name (str): The field name to promote.
        """
        if name in self._promoted_fields:
            return

        definition = self._fields.get(name)
        if definition is None:
            return

        if definition.field_type == FieldType.BOOL:
            return

        data_type = FIELD_PORT_DATA_TYPES.get(
            definition.field_type, PortDataType.VECTOR4
        )
        port = self.add_port(PortType.INPUT, name, data_type)
        port.set_color(DATA_TYPE_COLORS[data_type])
        self._promoted_fields[name] = port

    def demote_field(self, name: str) -> None:
        """
        Demote a promoted field back to a regular field, removing its
        input port.

        Args:
            name (str): The field name to demote.
        """
        port = self._promoted_fields.pop(name, None)
        if port is None:
            return
        self.remove_port(port)

    def get_field_value(self, name: str) -> Any:
        """
        Return the current value of a field. If the field is promoted and
        its port is connected, returns the mean of the upstream image instead.

        Args:
            name (str): The field's identifier key.
        Returns:
            Any: The current value, either from the upstream port or the field.
        """
        port = self._promoted_fields.get(name)
        if port is None or not port.wires:
            return self._field_values[name]

        for wire in port.wires:
            source_node = wire.source.parentItem()
            if not isinstance(source_node, CatenaNode):
                continue

            evaluated = source_node.evaluate()

            if evaluated is None or not isinstance(evaluated, numpy.ndarray):
                continue

            definition = self._fields.get(name)
            raw = float(evaluated.mean())

            if port.data_type in (
                PortDataType.FLOAT,
                PortDataType.INT,
                PortDataType.VECTOR1,
            ):
                return type(definition.default)(raw) if definition is not None else raw

            if definition is not None and definition.max_value is not None:
                return type(definition.default)(raw * definition.max_value)

            return raw

        return self._field_values[name]

    def is_promoted(self, name: str) -> bool:
        """
        Return whether a field is currently promoted to an input port.

        Args:
            name (str): The field name to check.
        Returns:
            bool: True if the field is promoted.
        """
        return name in self._promoted_fields

    def on_input_connection_changed(self, port: Port) -> None:
        """
        Called when a wire connecting to one of this node's input ports
        is created or destroyed.

        Args:
            port (Port): The input port whose connection changed.
        """
        pass

    def _resize_to_fit_ports(self) -> None:
        """Recompute body_height to fit all ports if not explicitly fixed."""
        input_count = sum(1 for p in self._ports if p.port_type == PortType.INPUT)
        output_count = sum(1 for p in self._ports if p.port_type == PortType.OUTPUT)
        max_count = max(input_count, output_count)

        required_height = (
            self._PORT_MARGIN * 2 + max(0, max_count - 1) * self._PORT_SPACING
        )

        if required_height > self.body_height:
            self.prepareGeometryChange()
            self.body_height = required_height
            self._update_wires()
            self.update()

    def mouseDoubleClickEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Called when the node is double-clicked. Opens the properties panel
        and sends this node's evaluated modifier to the tex_viewer.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        broker.emit(namespace.NODE_SELECTED, node=self)
        self._set_active_preview()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        broker.emit(namespace.NODE_SELECTED, node=self)
        super().mousePressEvent(event)

    def _set_active_preview(self) -> None:
        CatenaNode.active_preview_node = self
        if not self._preview_updates_suppressed():
            broker.emit(namespace.NODE_PREVIEW, image=self._preview_image())

    def _preview_image(self) -> Optional[numpy.ndarray]:
        """Return the image that should be shown in the texture viewer."""
        return self.evaluate()

    def _on_field_changed(self, node: "CatenaNode") -> None:
        if self._preview_updates_suppressed():
            return

        inputs = self.get_inputs()
        self._cached_value = self.process(inputs)

        if node is self and CatenaNode.active_preview_node is self:
            broker.emit(namespace.NODE_PREVIEW, image=self._preview_image())
        elif CatenaNode.active_preview_node is not None:
            broker.emit(
                namespace.NODE_PREVIEW,
                image=CatenaNode.active_preview_node._preview_image(),
            )

    def set_field_value(self, name: str, value: object) -> None:
        """
        Set the value of a field and emit NODE_FIELD_CHANGED.

        Args:
            name (str): The field's identifier key.
            value (object): The new value.
        """
        super().set_field_value(name, value)
        self._invalidate_downstream()
        self._on_field_changed(self)
        self._refresh_downstream_write_nodes()

    def _invalidate_downstream(self) -> None:
        """Clear the cached value of this node and everything downstream of it."""
        self._cached_value = None

        for port in self.output_ports():
            for wire in port.wires:
                target_node = wire.target.parentItem()
                if isinstance(target_node, CatenaNode):
                    target_node._invalidate_downstream()

    def _refresh_downstream_write_nodes(self) -> None:
        """
        Refresh downstream nodes that need eager recomputation.

        Write nodes need this so their file/model previews stay current.
        Nodes with connected promoted fields also need it, so field-driven
        inputs pick up upstream changes even when nothing is actively previewed.
        """
        if self._preview_updates_suppressed():
            return

        visited: set[CatenaNode] = set()
        stack: list[CatenaNode] = [self]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)

            promoted_ports = current._promoted_fields.values()
            if any(port.wires for port in promoted_ports):
                current.evaluate()

            if hasattr(current, "_emit_preview_update"):
                current._emit_preview_update()

            for output_port in current.output_ports():
                for wire in output_port.wires:
                    target_node = wire.target.parentItem()
                    if isinstance(target_node, CatenaNode):
                        stack.append(target_node)

    def get_inputs(self) -> dict[str, Optional[numpy.ndarray]]:
        """
        Evaluate all connected upstream nodes, keyed by input port name.

        Returns:
            dict[str, numpy.ndarray | None]: Evaluated modifier for each input
                port name. Unconnected ports map to None.
        """
        results: dict[str, Optional[numpy.ndarray]] = {}

        for port in self.input_ports():
            value = None

            for wire in port.wires:
                source_node = wire.source.parentItem()
                if isinstance(source_node, CatenaNode):
                    evaluated = source_node.evaluate()
                    if isinstance(evaluated, dict):
                        value = evaluated.get(wire.source.name)
                    else:
                        value = evaluated
                    break

            results[port.name] = value

        return results

    def evaluate(self) -> Optional[numpy.ndarray]:
        """
        Evaluate this node, pulling all upstream inputs as needed.

        Returns:
            numpy.ndarray | None: The processed output of this node.
        """
        if self._cached_value is None:
            inputs = self.get_inputs()
            self._cached_value = self.process(inputs)

        return self._cached_value

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Override in derived node classes to process incoming modifier data.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Evaluated images keyed
                by input port name. Empty for nodes with no input ports
                (e.g. a Panel/source node).
        Returns:
            numpy.ndarray | None: The processed modifier to pass downstream.
        """
        return None
