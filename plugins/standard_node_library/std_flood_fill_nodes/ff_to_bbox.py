from typing import Optional

import cv2
import numpy

from catena import api
from std_flood_fill_nodes import IMAGE_NODE_COLOR


class FloodFillToBBoxNode(api.CatenaNode):
    """
    A node that shades each flood fill region by its bounding box size.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Flood Fill to BBox Size")

    def _build(self) -> None:
        self.port_in = self.add_port(
            api.PortType.INPUT, "Flood Fill", api.PortDataType.FLOOD_FILL
        )
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Shade each connected region in a flood fill modifier by the size of its
        bounding box.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Flood Fill"
                containing a float32 flood fill modifier.
        Returns:
            numpy.ndarray | None: A float32 modifier of shape (H, W, 4) where
                each region is shaded in greyscale based on its bounding box size.
        """
        image = inputs.get("Flood Fill")
        if image is None:
            return None

        source = image.mean(axis=2) if image.ndim == 3 else image
        mask = numpy.round(source * 65535).astype(numpy.int32)

        unique_values = numpy.unique(mask)
        unique_values = unique_values[unique_values > 0]

        height, width = source.shape[:2]
        result = numpy.zeros((height, width, 4), dtype=numpy.float32)

        if len(unique_values) == 0:
            return result

        _, labels = cv2.connectedComponents(
            (mask > 0).astype(numpy.uint8), connectivity=4
        )

        bbox_sizes: list[tuple[int, float]] = []
        for label in range(1, labels.max() + 1):
            region = labels == label
            if not numpy.any(region):
                continue

            ys, xs = numpy.where(region)
            bbox_width = int(xs.max() - xs.min() + 1)
            bbox_height = int(ys.max() - ys.min() + 1)
            bbox_area = float(bbox_width * bbox_height)
            bbox_sizes.append((label, bbox_area))

        if not bbox_sizes:
            return result

        sizes = numpy.array([size for _, size in bbox_sizes], dtype=numpy.float32)
        size_min = float(sizes.min())
        size_max = float(sizes.max())
        size_range = size_max - size_min

        if size_range < 1e-6:
            normalized = numpy.full_like(sizes, 0.5, dtype=numpy.float32)
        else:
            normalized = ((sizes - size_min) / size_range).astype(numpy.float32)

        for (label, _), value in zip(bbox_sizes, normalized):
            result[labels == label] = value

        return result
