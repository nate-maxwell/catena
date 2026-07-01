from typing import Optional

import numpy

from catena import api
from std_graph_nodes import IMAGE_NODE_COLOR


class ResolutionNode(api.CatenaNode):
    """A node that returns the x and y resolution of the input image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Resolution")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out_x = self.add_port(
            api.PortType.OUTPUT, "X", api.PortDataType.FLOAT
        )
        self.port_out_y = self.add_port(
            api.PortType.OUTPUT, "Y", api.PortDataType.FLOAT
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[dict[str, Optional[numpy.ndarray]]]:
        """
        Return the width and height of the connected input image.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing an image. If no image is connected, the current
                texture resolution is returned instead.
        Returns:
            dict[str, numpy.ndarray | None] | None: Solid float32 images for
            the X and Y resolution values.
        """

        image = inputs.get("Input")
        if image is not None:
            image_array = numpy.asarray(image)
            if image_array.ndim >= 2:
                height, width = image_array.shape[:2]
            else:
                width, height = api.get_texture_resolution()
        else:
            width, height = api.get_texture_resolution()

        x_value = numpy.full((1, 1, 4), float(width), dtype=numpy.float32)
        y_value = numpy.full((1, 1, 4), float(height), dtype=numpy.float32)

        return {"X": x_value, "Y": y_value}
