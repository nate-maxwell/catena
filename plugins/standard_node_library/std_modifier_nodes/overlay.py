from typing import Optional

import cv2
import numpy

from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class OverlayNode(api.CatenaNode):
    """A node that overlays a top modifier onto a bottom modifier using an alpha mask."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Overlay")

    def _build(self) -> None:
        self.port_in_bottom = self.add_port(api.PortType.INPUT, "Bottom")
        self.port_in_top = self.add_port(api.PortType.INPUT, "Top")
        self.port_in_alpha = self.add_port(api.PortType.INPUT, "Alpha")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="mix",
                label="Mix",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=1.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Overlay a top modifier onto a bottom modifier using an optional alpha mask.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "Bottom",
                "Top", and optionally "Alpha", each containing float32 images.
        Returns:
            numpy.ndarray | None: The composited float32 modifier, or None if
                both Bottom and Top are None.
        """
        mix = self.get_field_value("mix")
        bottom = inputs.get("Bottom")
        top = inputs.get("Top")
        alpha = inputs.get("Alpha")

        if bottom is None and top is None:
            return None
        if bottom is None:
            return top
        if top is None:
            return bottom

        if top.shape != bottom.shape:
            height, width = bottom.shape[:2]
            top = cv2.resize(top, (width, height))

        if alpha is None:
            mask = numpy.full(bottom.shape[:2], mix, dtype=numpy.float32)
        else:
            if alpha.shape[:2] != bottom.shape[:2]:
                height, width = bottom.shape[:2]
                alpha = cv2.resize(alpha, (width, height))
            if alpha.ndim == 3:
                alpha = alpha.mean(axis=2)
            mask = alpha.astype(numpy.float32) * mix

        mask = mask[:, :, None]

        result = (
            bottom.astype(numpy.float32) * (1.0 - mask)
            + top.astype(numpy.float32) * mask
        )
        return result.astype(numpy.float32)
