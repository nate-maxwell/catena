from typing import Optional

import cv2
import numpy

from catena import api
from std_math_nodes import IMAGE_NODE_COLOR
from catena.api import resize_like

_PORT_TYPES = [v for k, v in vars(api.PortDataType).items() if not k.startswith("_")]


class AddNode(api.CatenaNode):
    """A node that adds two input images together."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Add")

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

    def _on_field_changed(self, node: "AddNode") -> None:
        data_type = self.get_field_value("data_type")

        self.port_in_a.data_type = data_type
        self.port_in_b.data_type = data_type
        self.port_out.data_type = data_type

        self.port_in_a.set_color(api.DATA_TYPE_COLORS[data_type])
        self.port_in_b.set_color(api.DATA_TYPE_COLORS[data_type])
        self.port_out.set_color(api.DATA_TYPE_COLORS[data_type])

        super()._on_field_changed(node)

    @staticmethod
    def _resize_to_match(
        source: numpy.ndarray, height: int, width: int
    ) -> numpy.ndarray:
        if source.shape[:2] == (height, width):
            return source.astype(numpy.float32)
        return cv2.resize(source, (width, height)).astype(numpy.float32)

    @staticmethod
    def _combine_scalar_like(
        image_a: numpy.ndarray, image_b: numpy.ndarray
    ) -> numpy.ndarray:
        if image_a.shape != image_b.shape:
            height, width = image_a.shape[:2]
            image_b = cv2.resize(image_b, (width, height))
        return (image_a + image_b).astype(numpy.float32)

    @staticmethod
    def _combine_vector(
        image_a: numpy.ndarray, image_b: numpy.ndarray
    ) -> numpy.ndarray:
        if image_a.shape != image_b.shape:
            height, width = image_a.shape[:2]
            image_b = cv2.resize(image_b, (width, height))
        return (image_a + image_b).astype(numpy.float32)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Add two input images together.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "A" and "B",
                each containing a float32 modifier. Values may exceed [0, 1] and
                should be clamped downstream if needed.
        Returns:
            numpy.ndarray | None: The summed float32 modifier, or whichever
                input is non-None if only one is provided.
        """
        image_a = inputs.get("A")
        image_b = inputs.get("B")
        data_type = self.get_field_value("data_type")

        if image_a is None and image_b is None:
            return None
        if image_a is None:
            return image_b
        if image_b is None:
            return image_a

        if image_a.shape != image_b.shape:
            image_b = resize_like(image_b, image_a)

        if data_type in (api.PortDataType.FLOAT, api.PortDataType.INT, api.PortDataType.VECTOR1):
            if image_a.ndim == 3:
                image_a = image_a.mean(axis=2, keepdims=True)
            if image_b.ndim == 3:
                image_b = image_b.mean(axis=2, keepdims=True)
            result = image_a + image_b
        else:
            result = image_a + image_b

        return result.astype(numpy.float32)
