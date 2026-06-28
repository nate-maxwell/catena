from typing import Optional

import cv2
import numpy

from catena import api
from std_generate_nodes.generator import GeneratorNode

_FADE_MODES = ["None", "Start", "End", "Start + End"]


class ScratchesNode(GeneratorNode):
    """A node that generates a scratches pattern."""

    def __init__(self) -> None:
        self._processor = ScratchesProcessor()
        super().__init__(title="Scratches")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="sp_count",
                label="Number",
                field_type=api.FieldType.INT,
                default=50,
                min_value=1,
                max_value=512,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="max_segments",
                label="Max Segments",
                field_type=api.FieldType.INT,
                default=16,
                min_value=2,
                max_value=256,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="rotation",
                label="Rotation",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="rotation_random",
                label="Rotation Random",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="scale",
                label="Scale",
                field_type=api.FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="scale_random",
                label="Scale Random",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="distortion",
                label="Distortion",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="distortion_random",
                label="Distortion Random",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="distortion_frequency",
                label="Distortion Frequency",
                field_type=api.FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="width",
                label="Width",
                field_type=api.FieldType.FLOAT,
                default=0.002,
                min_value=0.0,
                max_value=0.05,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="width_random",
                label="Width Random",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="position_random",
                label="Position Random",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="luminance_random",
                label="Luminance Random",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="fade_mode",
                label="Fade Mode",
                field_type=api.FieldType.CHOICE,
                default="None",
                options=_FADE_MODES,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="fade_length",
                label="Fade Length",
                field_type=api.FieldType.FLOAT,
                default=0.2,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="seed",
                label="Seed",
                field_type=api.FieldType.INT,
                default=0,
                min_value=0,
                max_value=99999,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a scratches pattern with highly customizable sp properties.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 scratches modifier of shape
                (height, width, 3) with values in [0, 1].
        """
        sp_count = self.get_field_value("sp_count")
        max_segments = self.get_field_value("max_segments")
        rotation = self.get_field_value("rotation")
        rotation_random = self.get_field_value("rotation_random")
        scale = self.get_field_value("scale")
        scale_random = self.get_field_value("scale_random")
        distortion = self.get_field_value("distortion")
        distortion_random = self.get_field_value("distortion_random")
        distortion_frequency = self.get_field_value("distortion_frequency")
        sp_width = self.get_field_value("width")
        width_random = self.get_field_value("width_random")
        position_random = self.get_field_value("position_random")
        luminance_random = self.get_field_value("luminance_random")
        fade_mode = self.get_field_value("fade_mode")
        fade_length = self.get_field_value("fade_length")
        seed = self.get_field_value("seed")
        seed = int(seed * 255) if isinstance(seed, float) else int(seed)
        width, height = api.get_texture_resolution()
        size = width

        rng = numpy.random.default_rng(seed)
        canvas = numpy.zeros((height, width), dtype=numpy.float32)

        sp_width_px = max(1, int(sp_width * size))

        for _ in range(sp_count):
            angle = rotation * 360.0 + rng.uniform(
                -rotation_random * 180.0,
                rotation_random * 180.0,
            )
            radians = numpy.deg2rad(angle)

            sp_scale = scale * (1.0 + rng.uniform(-scale_random, scale_random))
            sp_scale = numpy.clip(sp_scale, 0.01, 2.0)
            sp_length = int(sp_scale * size)

            local_distortion = distortion * (
                1.0 + rng.uniform(-distortion_random, distortion_random)
            )
            local_distortion = max(0.0, local_distortion)

            local_width = sp_width_px * (1.0 + rng.uniform(-width_random, width_random))
            local_width = max(1, int(local_width))

            luminance = 1.0 - rng.uniform(0.0, luminance_random)

            if position_random < 1.0:
                cx = int(width / 2 + rng.uniform(-1, 1) * position_random * width / 2)
                cy = int(height / 2 + rng.uniform(-1, 1) * position_random * height / 2)
            else:
                cx = rng.integers(0, width)
                cy = rng.integers(0, height)

            freq = max(0.01, distortion_frequency) * 0.1
            phase = rng.uniform(0, numpy.pi * 2)

            points = []
            segments = min(max_segments, max(2, sp_length))
            for i in range(segments):
                t = i / (segments - 1)
                dist = t * sp_length

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
                if fade_mode in ("Start", "Start + End"):
                    fade_t = min(t / max(fade_length, 0.001), 1.0)
                    seg_luminance *= fade_t
                if fade_mode in ("End", "Start + End"):
                    fade_t = min((1.0 - t) / max(fade_length, 0.001), 1.0)
                    seg_luminance *= fade_t

                cv2.line(
                    canvas,
                    p1,
                    p2,
                    float(seg_luminance),
                    local_width,
                )

        return numpy.repeat(canvas[:, :, None], 4, axis=2).astype(numpy.float32)
