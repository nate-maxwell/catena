from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.transform import IMAGE_NODE_COLOR


class ScatterNode(CatenaNode):
    """A node that scatters copies of an input image at random positions."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Scatter")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="count",
                label="Count",
                field_type=FieldType.INT,
                default=10,
                min_value=1,
                max_value=500,
            )
        )
        self.add_field(
            FieldDefinition(
                name="scale",
                label="Scale",
                field_type=FieldType.FLOAT,
                default=0.2,
                min_value=0.01,
                max_value=2.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="scale_variance",
                label="Scale Variance",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="rotation_variance",
                label="Rotation Variance",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=360.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="seed",
                label="Seed",
                field_type=FieldType.INT,
                default=0,
                min_value=0,
                max_value=99999,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        count = self.get_field_value("count")
        scale = self.get_field_value("scale")
        scale_variance = self.get_field_value("scale_variance")
        rotation_variance = self.get_field_value("rotation_variance")
        seed = self.get_field_value("seed")

        height, width = image.shape[:2]
        rng = numpy.random.default_rng(seed)

        canvas = numpy.zeros((height, width, 3), dtype=numpy.float32)

        for _ in range(count):
            local_scale = scale * (1.0 + rng.uniform(-scale_variance, scale_variance))
            local_scale = max(local_scale, 0.01)

            stamp_w = max(1, int(width * local_scale))
            stamp_h = max(1, int(height * local_scale))

            stamp = cv2.resize(image, (stamp_w, stamp_h))

            rotation = rng.uniform(-rotation_variance, rotation_variance)
            if rotation != 0.0:
                center = (stamp_w / 2.0, stamp_h / 2.0)
                matrix = cv2.getRotationMatrix2D(center, rotation, 1.0)
                stamp = cv2.warpAffine(stamp, matrix, (stamp_w, stamp_h))

            cx = rng.integers(0, width)
            cy = rng.integers(0, height)

            x0 = cx - stamp_w // 2
            y0 = cy - stamp_h // 2
            x1 = x0 + stamp_w
            y1 = y0 + stamp_h

            src_x0 = max(0, -x0)
            src_y0 = max(0, -y0)
            src_x1 = stamp_w - max(0, x1 - width)
            src_y1 = stamp_h - max(0, y1 - height)

            dst_x0 = max(0, x0)
            dst_y0 = max(0, y0)
            dst_x1 = min(width, x1)
            dst_y1 = min(height, y1)

            if src_x1 > src_x0 and src_y1 > src_y0:
                region = stamp[src_y0:src_y1, src_x0:src_x1]
                canvas[dst_y0:dst_y1, dst_x0:dst_x1] = numpy.maximum(
                    canvas[dst_y0:dst_y1, dst_x0:dst_x1], region
                )

        return canvas.astype(numpy.float32)
