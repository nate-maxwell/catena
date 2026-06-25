from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences

_FADE_MODES = ["None", "Start", "End", "Start + End"]


class ScratchesProcessor(ProcessorNode):
    """A headless processor that generates a scratches pattern."""

    def __init__(
        self,
        spline_count: int = 50,
        max_segments: int = 16,
        rotation: float = 0.0,
        rotation_random: float = 1.0,
        scale: float = 0.5,
        scale_random: float = 0.0,
        distortion: float = 0.0,
        distortion_random: float = 0.0,
        distortion_frequency: float = 0.5,
        width: float = 0.002,
        width_random: float = 0.0,
        position_random: float = 1.0,
        luminance_random: float = 0.0,
        fade_mode: str = "None",
        fade_length: float = 0.2,
        seed: int = 0,
    ) -> None:
        super().__init__()
        self.spline_count = spline_count
        self.max_segments = max_segments
        self.rotation = rotation
        self.rotation_random = rotation_random
        self.scale = scale
        self.scale_random = scale_random
        self.distortion = distortion
        self.distortion_random = distortion_random
        self.distortion_frequency = distortion_frequency
        self.width = width
        self.width_random = width_random
        self.position_random = position_random
        self.luminance_random = luminance_random
        self.fade_mode = fade_mode
        self.fade_length = fade_length
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a scratches pattern with highly customizable spline properties.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 scratches modifier of shape
                (height, width, 3) with values in [0, 1].
        """
        size = preferences.Preferences().general_preferences.texture_resolution
        height = size
        width = size

        rng = numpy.random.default_rng(self.seed)
        canvas = numpy.zeros((height, width), dtype=numpy.float32)

        spline_width_px = max(1, int(self.width * size))

        for _ in range(self.spline_count):
            angle = self.rotation * 360.0 + rng.uniform(
                -self.rotation_random * 180.0,
                self.rotation_random * 180.0,
            )
            radians = numpy.deg2rad(angle)

            spline_scale = self.scale * (
                1.0 + rng.uniform(-self.scale_random, self.scale_random)
            )
            spline_scale = numpy.clip(spline_scale, 0.01, 2.0)
            spline_length = int(spline_scale * size)

            local_distortion = self.distortion * (
                1.0 + rng.uniform(-self.distortion_random, self.distortion_random)
            )
            local_distortion = max(0.0, local_distortion)

            local_width = spline_width_px * (
                1.0 + rng.uniform(-self.width_random, self.width_random)
            )
            local_width = max(1, int(local_width))

            luminance = 1.0 - rng.uniform(0.0, self.luminance_random)

            if self.position_random < 1.0:
                cx = int(
                    width / 2 + rng.uniform(-1, 1) * self.position_random * width / 2
                )
                cy = int(
                    height / 2 + rng.uniform(-1, 1) * self.position_random * height / 2
                )
            else:
                cx = rng.integers(0, width)
                cy = rng.integers(0, height)

            freq = max(0.01, self.distortion_frequency) * 0.1
            phase = rng.uniform(0, numpy.pi * 2)

            points = []
            segments = min(self.max_segments, max(2, spline_length))
            for i in range(segments):
                t = i / (segments - 1)
                dist = t * spline_length

                wave = numpy.sin(dist * freq + phase) * local_distortion * size * 0.05

                px = (
                    int(cx + numpy.cos(radians) * dist + numpy.sin(radians) * wave)
                    % width
                )
                py = (
                    int(cy + numpy.sin(radians) * dist - numpy.cos(radians) * wave)
                    % height
                )
                points.append((px, py))

            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]

                if abs(p1[0] - p2[0]) > width // 2 or abs(p1[1] - p2[1]) > height // 2:
                    continue

                t = i / max(len(points) - 1, 1)

                seg_luminance = luminance
                if self.fade_mode in ("Start", "Start + End"):
                    fade_t = min(t / max(self.fade_length, 0.001), 1.0)
                    seg_luminance *= fade_t
                if self.fade_mode in ("End", "Start + End"):
                    fade_t = min((1.0 - t) / max(self.fade_length, 0.001), 1.0)
                    seg_luminance *= fade_t

                cv2.line(
                    canvas,
                    p1,
                    p2,
                    float(seg_luminance),
                    local_width,
                )

        return numpy.repeat(canvas[:, :, None], 4, axis=2).astype(numpy.float32)


class ScratchesNode(GeneratorNode):
    """A node that generates a scratches pattern."""

    def __init__(self) -> None:
        self._processor = ScratchesProcessor()
        super().__init__(title="Scratches")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="spline_count",
                label="Number",
                field_type=FieldType.INT,
                default=50,
                min_value=1,
                max_value=512,
            )
        )
        self.add_field(
            FieldDefinition(
                name="max_segments",
                label="Max Segments",
                field_type=FieldType.INT,
                default=16,
                min_value=2,
                max_value=256,
            )
        )
        self.add_field(
            FieldDefinition(
                name="rotation",
                label="Rotation",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="rotation_random",
                label="Rotation Random",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="scale",
                label="Scale",
                field_type=FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="scale_random",
                label="Scale Random",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="distortion",
                label="Distortion",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="distortion_random",
                label="Distortion Random",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="distortion_frequency",
                label="Distortion Frequency",
                field_type=FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="width",
                label="Width",
                field_type=FieldType.FLOAT,
                default=0.002,
                min_value=0.0,
                max_value=0.05,
            )
        )
        self.add_field(
            FieldDefinition(
                name="width_random",
                label="Width Random",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="position_random",
                label="Position Random",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="luminance_random",
                label="Luminance Random",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="fade_mode",
                label="Fade Mode",
                field_type=FieldType.CHOICE,
                default="None",
                options=_FADE_MODES,
            )
        )
        self.add_field(
            FieldDefinition(
                name="fade_length",
                label="Fade Length",
                field_type=FieldType.FLOAT,
                default=0.2,
                min_value=0.0,
                max_value=1.0,
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
        self._processor.spline_count = self.get_field_value("spline_count")
        self._processor.max_segments = self.get_field_value("max_segments")
        self._processor.rotation = self.get_field_value("rotation")
        self._processor.rotation_random = self.get_field_value("rotation_random")
        self._processor.scale = self.get_field_value("scale")
        self._processor.scale_random = self.get_field_value("scale_random")
        self._processor.distortion = self.get_field_value("distortion")
        self._processor.distortion_random = self.get_field_value("distortion_random")
        self._processor.distortion_frequency = self.get_field_value(
            "distortion_frequency"
        )
        self._processor.width = self.get_field_value("width")
        self._processor.width_random = self.get_field_value("width_random")
        self._processor.position_random = self.get_field_value("position_random")
        self._processor.luminance_random = self.get_field_value("luminance_random")
        self._processor.fade_mode = self.get_field_value("fade_mode")
        self._processor.fade_length = self.get_field_value("fade_length")

        seed = self.get_field_value("seed")
        self._processor.seed = int(seed * 255) if isinstance(seed, float) else int(seed)

        return self._processor.process(inputs)
