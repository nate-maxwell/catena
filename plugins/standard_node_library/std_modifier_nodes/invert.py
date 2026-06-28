from typing import Optional

import numpy

from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class InvertNode(api.CatenaNode):
    """A node that inverts the colors of an input modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Invert")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Invert the colors of an input modifier.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier with values in [0, 1].
        Returns:
            numpy.ndarray | None: The inverted float32 modifier.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        return (1.0 - image).astype(numpy.float32)
