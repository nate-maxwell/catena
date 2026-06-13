from typing import Optional

import broker
import numpy
from PySide6 import QtWidgets
from PySide6TK.Nodes import BaseNode
from PySide6TK.Nodes import Port
from PySide6TK.Nodes import PortType

from catena.core import namespace


class CatenaNode(BaseNode):

    active_preview_node: Optional["CatenaNode"] = None

    def __init__(self, title: str, width: int = 160, body_height: int = 40) -> None:
        super().__init__(title, width, body_height)
        self._is_active_preview: bool = False
        broker.register_subscriber(namespace.NODE_FIELD_CHANGED, self._on_field_changed)

    def add_port(self, port_type: str, name: str) -> Port:
        """
        Create and position a port on this node.

        Input ports are placed on the left edge, output ports on the right.
        Ports are stacked top-to-bottom in the order they are added.

        Args:
            port_type (str): Either ``PortType.INPUT`` or ``PortType.OUTPUT``.
            name (str): Display name for the port.
        Returns:
            Port: The created port.
        """
        input_count = sum(1 for p in self._ports if p.port_type == PortType.INPUT)
        output_count = sum(1 for p in self._ports if p.port_type == PortType.OUTPUT)

        port = Port(port_type, name, self)
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

        return port

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
        and sends this node's evaluated image to the viewport.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        broker.emit(namespace.NODE_DOUBLE_CLICK, node=self)
        self._set_active_preview()
        super().mouseDoubleClickEvent(event)

    def _set_active_preview(self) -> None:
        CatenaNode.active_preview_node = self
        broker.emit(namespace.NODE_PREVIEW, image=self.evaluate())

    def _on_field_changed(self, node: "CatenaNode", name: str, value: object) -> None:
        # dead args are required to meet subscription signature
        if node is self and CatenaNode.active_preview_node is self:
            broker.emit(namespace.NODE_PREVIEW, image=self.evaluate())

    def set_field_value(self, name: str, value: object) -> None:
        """
        Set the value of a field and emit NODE_FIELD_CHANGED.

        Args:
            name (str): The field's identifier key.
            value (object): The new value.
        """
        super().set_field_value(name, value)
        broker.emit(namespace.NODE_FIELD_CHANGED, node=self, name=name, value=value)

    def get_inputs(self) -> dict[str, Optional[numpy.ndarray]]:
        """
        Evaluate all connected upstream nodes, keyed by input port name.

        Returns:
            dict[str, numpy.ndarray | None]: Evaluated image for each input
                port name. Unconnected ports map to None.
        """
        results: dict[str, Optional[numpy.ndarray]] = {}

        for port in self.input_ports():
            value = None

            for wire in port.wires:
                source_node = wire.source.parentItem()
                if isinstance(source_node, CatenaNode):
                    value = source_node.evaluate()
                    break

            results[port.name] = value

        return results

    def evaluate(self) -> Optional[numpy.ndarray]:
        """
        Evaluate this node, pulling all upstream inputs as needed.

        Returns:
            numpy.ndarray | None: The processed output of this node.
        """
        inputs = self.get_inputs()
        return self.process(inputs)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Override in derived node classes to process incoming image data.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Evaluated images keyed
                by input port name. Empty for nodes with no input ports
                (e.g. a Panel/source node).
        Returns:
            numpy.ndarray | None: The processed image to pass downstream.
        """
        return None
