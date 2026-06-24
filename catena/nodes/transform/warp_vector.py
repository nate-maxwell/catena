from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.transform import IMAGE_NODE_COLOR
from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode


class VectorWarpProcessor(ProcessorNode):
    """A headless processor that displaces pixels using a 2-channel vector displacement map."""

    def __init__(
        self,
        strength: float = 10.0,
    ) -> None:
        super().__init__()
        self.strength = strength

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Displace pixels using a vector displacement map. The red channel of
        the displacement image drives horizontal offset and the green channel
        drives vertical offset. Both channels are remapped from [0, 1] to
        [-1, 1] so that 0.5 grey means no displacement.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "Input"
                and "Displacement", each a float32 BGR image. If no
                displacement is provided the input is returned unchanged.
        Returns:
            numpy.ndarray | None: The warped float32 image, or None if no
                input is provided.
        """
        image = inputs.get("Input")
        displacement = inputs.get("Displacement")

        if image is None:
            return None

        if displacement is None or self.strength <= 0:
            return image

        height, width = image.shape[:2]

        if displacement.shape[:2] != (height, width):
            displacement = cv2.resize(displacement, (width, height))

        # BGR: index 2 = R channel (X), index 1 = G channel (Y)
        # Remap [0, 1] -> [-1, 1] so 0.5 = no displacement
        offset_x = (displacement[:, :, 2] * 2.0 - 1.0) * self.strength
        offset_y = (displacement[:, :, 1] * 2.0 - 1.0) * self.strength

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
        map_x = (x_idx + offset_x).astype(numpy.float32)
        map_y = (y_idx + offset_y).astype(numpy.float32)

        result = cv2.remap(
            image,
            map_x,
            map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT,
        )
        return result.astype(numpy.float32)


class VectorWarpNode(CatenaNode):
    """A node that displaces pixels using a 2-channel vector displacement map."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = VectorWarpProcessor()
        super().__init__(title="Vector Warp")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_in_displacement = self.add_port(PortType.INPUT, "Displacement")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="strength",
                label="Strength",
                field_type=FieldType.FLOAT,
                default=10.0,
                min_value=0.0,
                max_value=10000.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.strength = self.get_field_value("strength")
        return self._processor.process(inputs)
