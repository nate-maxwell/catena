from typing import Optional

import numpy

from catena import api
from std_math_nodes import IMAGE_NODE_COLOR


class CeilNode(api.CatenaNode):
    """A node that applies a ceiling function to an input modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Ceil")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Apply a ceiling function to an input modifier, rounding each value up
        to the nearest integer.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier with values in [0, 1].
        Returns:
            numpy.ndarray | None: The ceiled float32 modifier.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        return numpy.ceil(image).astype(numpy.float32)
