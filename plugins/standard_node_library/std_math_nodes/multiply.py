from typing import Optional

import cv2
import numpy

from catena import api
from std_math_nodes import IMAGE_NODE_COLOR
from catena.api import resize_like

_PORT_TYPES = [v for k, v in vars(api.PortDataType).items() if not k.startswith("_")]


class MultiplyNode(api.CatenaNode):
    """A node that multiplies two input images together."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Multiply")

    def _build(self) -> None:
        self.port_in_a = self.add_port(api.PortType.INPUT, "A", api.PortDataType.VECTOR4)
        self.port_in_b = self.add_port(api.PortType.INPUT, "B", api.PortDataType.VECTOR4)
        self.port_out = self.add_port(
            api.PortType.OUTPUT, "Output", api.PortDataType.VECTOR4
        )

        self.add_field(
            api.FieldDefinition(
                name="data_type",
                label="Type",
                field_type=api.FieldType.CHOICE,
                default=api.PortDataType.VECTOR4,
                options=_PORT_TYPES,
            )
        )

    def _on_field_changed(self, node: "MultiplyNode") -> None:
        data_type = self.get_field_value("data_type")
        for port in (self.port_in_a, self.port_in_b, self.port_out):
            port.data_type = data_type
            port.set_color(api.DATA_TYPE_COLORS[data_type])

        super()._on_field_changed(node)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Multiply two input images together per-pixel.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "A" and "B",
                each containing a float32 modifier. Both must be connected.
        Returns:
            numpy.ndarray | None: The multiplied float32 modifier, or None if
                either input is missing.
        """
        image_a = inputs.get("A")
        image_b = inputs.get("B")
        data_type = self.get_field_value("data_type")

        if image_a is None or image_b is None:
            return None

        if image_a.shape != image_b.shape:
            image_b = resize_like(image_b, image_a)

        if data_type in (api.PortDataType.FLOAT, api.PortDataType.INT, api.PortDataType.VECTOR1):
            if image_a.ndim == 3:
                image_a = image_a.mean(axis=2, keepdims=True)
            if image_b.ndim == 3:
                image_b = image_b.mean(axis=2, keepdims=True)

        return (image_a * image_b).astype(numpy.float32)
