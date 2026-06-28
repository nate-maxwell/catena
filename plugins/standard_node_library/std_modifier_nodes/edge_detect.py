from typing import Optional

import cv2
import numpy

from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class EdgeDetectNode(api.CatenaNode):
    """A node that detects edges in an input modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Edge Detect")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="edge_width",
                label="Edge Width",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=1.0,
                max_value=50.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="roundedness",
                label="Roundedness",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="invert",
                label="Invert",
                field_type=api.FieldType.BOOL,
                default=False,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="tolerance",
                label="Tolerance",
                field_type=api.FieldType.FLOAT,
                default=0.1,
                min_value=0.0,
                max_value=1.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Detect edges in an input modifier using Sobel gradients.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier with values in [0, 1].
        Returns:
            numpy.ndarray | None: A float32 edge mask of shape (H, W, 3)
                with values in [0, 1].
        """

        edge_width = self.get_field_value("edge_width")
        roundedness = self.get_field_value("roundedness")
        invert = self.get_field_value("invert")
        tolerance = self.get_field_value("tolerance")

        image = inputs.get("Input")
        if image is None:
            return None

        gray = image.mean(axis=2) if image.ndim == 3 else image
        gray_uint8 = numpy.clip(gray * 255.0, 0, 255).astype(numpy.uint8)

        sobel_x = cv2.Sobel(gray_uint8, cv2.CV_32F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray_uint8, cv2.CV_32F, 0, 1, ksize=3)
        magnitude = numpy.sqrt(sobel_x**2 + sobel_y**2)
        magnitude = magnitude / (magnitude.max() + 1e-6)

        edges = numpy.clip((magnitude - tolerance) / (1.0 - tolerance + 1e-6), 0.0, 1.0)

        if edge_width > 1.0:
            kernel_size = int(edge_width) * 2 + 1
            if roundedness > 0.0:
                blur_radius = roundedness * edge_width
                edges = cv2.GaussianBlur(
                    edges, (0, 0), sigmaX=blur_radius, sigmaY=blur_radius
                )
            kernel = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
            )
            edges = cv2.dilate(edges, kernel)

        edges = numpy.clip(edges, 0.0, 1.0)

        if invert:
            edges = 1.0 - edges

        return numpy.repeat(edges[:, :, None], 4, axis=2).astype(numpy.float32)
