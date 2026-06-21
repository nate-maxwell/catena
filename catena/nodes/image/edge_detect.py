from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.image import IMAGE_NODE_COLOR


class EdgeDetectProcessor(ProcessorNode):
    """A headless processor that detects edges in an input image."""

    def __init__(
        self,
        edge_width: float = 1.0,
        roundedness: float = 0.0,
        invert: bool = False,
        tolerance: float = 0.1,
    ) -> None:
        super().__init__()
        self.edge_width = edge_width
        self.roundedness = roundedness
        self.invert = invert
        self.tolerance = tolerance

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Detect edges in an input image using Sobel gradients.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image with values in [0, 1].
        Returns:
            numpy.ndarray | None: A float32 edge mask of shape (H, W, 3)
                with values in [0, 1].
        """
        image = inputs.get("Input")
        if image is None:
            return None

        gray = image.mean(axis=2) if image.ndim == 3 else image
        gray_uint8 = numpy.clip(gray * 255.0, 0, 255).astype(numpy.uint8)

        sobel_x = cv2.Sobel(gray_uint8, cv2.CV_32F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray_uint8, cv2.CV_32F, 0, 1, ksize=3)
        magnitude = numpy.sqrt(sobel_x**2 + sobel_y**2)
        magnitude = magnitude / (magnitude.max() + 1e-6)

        edges = numpy.clip(
            (magnitude - self.tolerance) / (1.0 - self.tolerance + 1e-6), 0.0, 1.0
        )

        if self.edge_width > 1.0:
            kernel_size = int(self.edge_width) * 2 + 1
            if self.roundedness > 0.0:
                blur_radius = self.roundedness * self.edge_width
                edges = cv2.GaussianBlur(
                    edges, (0, 0), sigmaX=blur_radius, sigmaY=blur_radius
                )
            kernel = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
            )
            edges = cv2.dilate(edges, kernel)

        edges = numpy.clip(edges, 0.0, 1.0)

        if self.invert:
            edges = 1.0 - edges

        return numpy.repeat(edges[:, :, None], 3, axis=2).astype(numpy.float32)


class EdgeDetectNode(CatenaNode):
    """A node that detects edges in an input image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = EdgeDetectProcessor()
        super().__init__(title="Edge Detect")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="edge_width",
                label="Edge Width",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=1.0,
                max_value=50.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="roundedness",
                label="Roundedness",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="invert",
                label="Invert",
                field_type=FieldType.BOOL,
                default=False,
            )
        )
        self.add_field(
            FieldDefinition(
                name="tolerance",
                label="Tolerance",
                field_type=FieldType.FLOAT,
                default=0.1,
                min_value=0.0,
                max_value=1.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.edge_width = self.get_field_value("edge_width")
        self._processor.roundedness = self.get_field_value("roundedness")
        self._processor.invert = self.get_field_value("invert")
        self._processor.tolerance = self.get_field_value("tolerance")
        return self._processor.process(inputs)
