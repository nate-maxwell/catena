from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.modifier import IMAGE_NODE_COLOR
from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode


class AnisotropicBlurProcessor(ProcessorNode):
    """A headless processor that applies directional anisotropic blur."""

    def __init__(
        self,
        intensity: float = 4.0,
        anisotropy: float = 0.0,
        angle: float = 0.0,
        quality: int = 0,
    ) -> None:
        super().__init__()
        self.intensity = intensity
        self.anisotropy = anisotropy
        self.angle = angle
        self.quality = quality

    def _rotate(
        self,
        channel: numpy.ndarray,
        angle_deg: float,
        w: int,
        h: int,
    ) -> numpy.ndarray:
        """
        Rotate a single channel image using cv2.warpAffine.

        Args:
            channel (numpy.ndarray): Float32 array of shape (H, W).
            angle_deg (float): Rotation angle in degrees.
            w (int): Image width.
            h (int): Image height.
        Returns:
            numpy.ndarray: Rotated float32 array of shape (H, W).
        """
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle_deg, 1.0)
        return cv2.warpAffine(
            channel,
            M,
            (w, h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT,
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Apply anisotropic blur by rotating each channel into the blur axis
        frame, applying separable O(H*W) box/Gaussian passes, then rotating
        back. This is O(H*W) regardless of intensity, making large radius
        values fast.

        Angle 0-1 maps to 0-90 degrees. Quality 0 uses a box filter.
        Quality 1 adds a small Gaussian softening pass for smooth falloff.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Must contain key
                "Input" with a float32 BGR image.
        Returns:
            numpy.ndarray | None: A float32 BGR image of shape (H, W, 3)
                with values in [0, 1], or None if no input is provided.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        image = numpy.clip(image, 0.0, 1.0).astype(numpy.float32)

        if self.intensity < 0.5:
            return image.copy()

        h, w = image.shape[:2]
        r_main = max(1.0, self.intensity)
        r_perp = max(1.0, r_main * (1.0 - numpy.clip(self.anisotropy, 0.0, 1.0)))
        angle_deg = self.angle * 90.0

        kw = max(1, int(r_main)) * 2 + 1
        kh = max(1, int(r_perp)) * 2 + 1

        def process_channel(ch: numpy.ndarray) -> numpy.ndarray:
            rotated = self._rotate(ch, angle_deg, w, h)
            if self.quality == 1:
                blurred = cv2.GaussianBlur(
                    rotated,
                    (0, 0),
                    sigmaX=r_main / 3.0,
                    sigmaY=r_perp / 3.0,
                    borderType=cv2.BORDER_REFLECT,
                )
            else:
                blurred = cv2.boxFilter(
                    rotated, -1, (kw, kh), borderType=cv2.BORDER_REFLECT
                )
            return self._rotate(blurred, -angle_deg, w, h)

        result = numpy.stack(
            [process_channel(image[:, :, c]) for c in range(image.shape[2])],
            axis=2,
        )
        return numpy.clip(result, 0.0, 1.0)


class AnisotropicBlurNode(CatenaNode):
    """A node that applies directional anisotropic blur."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = AnisotropicBlurProcessor()
        super().__init__(title="Anisotropic Blur")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="intensity",
                label="Intensity",
                field_type=FieldType.FLOAT,
                default=4.0,
                min_value=0.0,
                max_value=999999.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="anisotropy",
                label="Anisotropy",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="angle",
                label="Angle",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="quality",
                label="Quality",
                field_type=FieldType.INT,
                default=0,
                min_value=0,
                max_value=1,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.intensity = self.get_field_value("intensity")
        self._processor.anisotropy = self.get_field_value("anisotropy")
        self._processor.angle = self.get_field_value("angle")
        self._processor.quality = self.get_field_value("quality")
        return self._processor.process(inputs)
