from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences


class GrungeProcessor(ProcessorNode):
    """A headless processor that generates a grunge noise map."""

    def __init__(
        self,
        balance: float = 0.5,
        contrast: float = 1.0,
        disorder: float = 0.5,
        seed: int = 0,
    ) -> None:
        super().__init__()
        self.balance = balance
        self.contrast = contrast
        self.disorder = disorder
        self.seed = seed

    def _value_noise(
        self,
        height: int,
        width: int,
        scale: float,
        rng: numpy.random.Generator,
    ) -> numpy.ndarray:
        grid_h = max(2, int(round(height / scale)))
        grid_w = max(2, int(round(width / scale)))
        lattice = rng.random((grid_h, grid_w)).astype(numpy.float32)
        return cv2.resize(lattice, (width, height), interpolation=cv2.INTER_LINEAR)

    def _perlin_noise(
        self,
        height: int,
        width: int,
        scale: float,
        octaves: int,
        rng: numpy.random.Generator,
    ) -> numpy.ndarray:
        total = numpy.zeros((height, width), dtype=numpy.float32)
        amplitude = 1.0
        max_amplitude = 0.0
        current_scale = scale

        for i in range(octaves):
            total += self._value_noise(height, width, current_scale, rng) * amplitude
            max_amplitude += amplitude
            amplitude *= 0.5
            current_scale = max(current_scale * 0.5, 2.0)

        return (total / max_amplitude).astype(numpy.float32)

    def _clouds_noise(
        self,
        height: int,
        width: int,
        scale: float,
        octaves: int,
        persistence: float,
        contrast: float,
        rng: numpy.random.Generator,
    ) -> numpy.ndarray:
        total = numpy.zeros((height, width), dtype=numpy.float32)
        amplitude = 1.0
        max_amplitude = 0.0
        current_scale = scale

        for i in range(octaves):
            total += self._value_noise(height, width, current_scale, rng) * amplitude
            max_amplitude += amplitude
            amplitude *= persistence
            current_scale = max(current_scale * 0.5, 2.0)

        total /= max_amplitude
        return numpy.clip((total - 0.5) * contrast + 0.5, 0.0, 1.0).astype(
            numpy.float32
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a grunge noise map by warping Perlin noise with clouds
        noise as displacement, then rotating the result.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 grunge modifier with values in [0, 1].
        """
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width

        rng = numpy.random.default_rng(self.seed)

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        perlin = self._perlin_noise(height, width, 256.0, 3, rng)
        perlin = numpy.clip((perlin - (53 / 255.0)) / (1.0 - 53 / 255.0), 0.0, 1.0)

        clouds = self._clouds_noise(height, width, 128.0, 3, 0.6, 1.5, rng)

        warp_strength_1 = 100.0 * self.disorder
        map_x = (x_idx + clouds * warp_strength_1).astype(numpy.float32)
        map_y = (y_idx + clouds * warp_strength_1).astype(numpy.float32)
        warped1 = cv2.remap(
            perlin, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
        )

        warp_strength_2 = 200.0 * self.disorder
        map_x2 = (x_idx + clouds * warp_strength_2).astype(numpy.float32)
        map_y2 = (y_idx + clouds * warp_strength_2).astype(numpy.float32)
        warped2 = cv2.remap(
            warped1, map_x2, map_y2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
        )

        center = (width / 2.0, height / 2.0)
        matrix = cv2.getRotationMatrix2D(center, 90.0, 1.0)
        result = cv2.warpAffine(
            warped2, matrix, (width, height), borderMode=cv2.BORDER_REFLECT
        )

        result -= result.min()
        if result.max() > 0:
            result /= result.max()

        result = numpy.clip((result - 0.5) * self.contrast + self.balance, 0.0, 1.0)

        return numpy.repeat(result[:, :, None], 4, axis=2).astype(numpy.float32)


class GrungeNode(GeneratorNode):
    """A node that generates a grunge noise map."""

    def __init__(self) -> None:
        self._processor = GrungeProcessor()
        super().__init__(title="Grunge")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="balance",
                label="Balance",
                field_type=FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="contrast",
                label="Contrast",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=5.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="disorder",
                label="Disorder",
                field_type=FieldType.FLOAT,
                default=0.5,
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
        self._processor.balance = self.get_field_value("balance")
        self._processor.contrast = self.get_field_value("contrast")
        self._processor.disorder = self.get_field_value("disorder")

        seed = self.get_field_value("seed")
        self._processor.seed = int(seed * 255) if isinstance(seed, float) else int(seed)

        return self._processor.process(inputs)
