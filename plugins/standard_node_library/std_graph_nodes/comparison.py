from typing import Optional

import cv2
import numpy

from catena import api
from std_graph_nodes import IMAGE_NODE_COLOR

_COMPARISON_TYPES = [
    "Greater Than",
    "Greater Than Or Equal",
    "Less Than",
    "Less Than Or Equal",
    "Equal To",
    "Not Equal To",
]


class ComparisonNode(api.CatenaNode):
    """A node that compares two inputs and outputs the result as a mask."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Comparison")

    def _build(self) -> None:
        self.port_in_a = self.add_port(api.PortType.INPUT, "A", api.PortDataType.VECTOR4)
        self.port_in_b = self.add_port(api.PortType.INPUT, "B", api.PortDataType.VECTOR4)
        self.port_out = self.add_port(api.PortType.OUTPUT, "Result")

        self.add_field(
            api.FieldDefinition(
                name="comparison_type",
                label="Comparison",
                field_type=api.FieldType.CHOICE,
                default="Greater Than",
                options=_COMPARISON_TYPES,
            )
        )

    @staticmethod
    def _prepare_inputs(
        image_a: numpy.ndarray, image_b: numpy.ndarray
    ) -> tuple[numpy.ndarray, numpy.ndarray]:
        if image_a.shape != image_b.shape:
            height, width = image_a.shape[:2]
            image_b = cv2.resize(image_b, (width, height))

        if image_a.ndim == 3:
            image_a = image_a.mean(axis=2)
        if image_b.ndim == 3:
            image_b = image_b.mean(axis=2)

        return image_a.astype(numpy.float32), image_b.astype(numpy.float32)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Compare two inputs element-wise and return a pixel mask.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "A" and "B",
                each containing a numeric modifier. Both inputs must be present.
        Returns:
            numpy.ndarray | None: A float32 mask with values of 0.0 or 1.0,
                or None if either input is missing.
        """
        image_a = inputs.get("A")
        image_b = inputs.get("B")

        if image_a is None or image_b is None:
            return None

        image_a, image_b = self._prepare_inputs(image_a, image_b)
        comparison_type = self.get_field_value("comparison_type")

        if comparison_type == "Greater Than":
            result = numpy.greater(image_a, image_b)
        elif comparison_type == "Greater Than Or Equal":
            result = numpy.greater_equal(image_a, image_b)
        elif comparison_type == "Less Than":
            result = numpy.less(image_a, image_b)
        elif comparison_type == "Less Than Or Equal":
            result = numpy.less_equal(image_a, image_b)
        elif comparison_type == "Equal To":
            result = numpy.isclose(image_a, image_b, atol=1e-6)
        elif comparison_type == "Not Equal To":
            result = numpy.logical_not(numpy.isclose(image_a, image_b, atol=1e-6))
        else:
            result = numpy.greater(image_a, image_b)

        mask = result.astype(numpy.float32)
        return numpy.repeat(mask[:, :, None], 4, axis=2).astype(numpy.float32)
