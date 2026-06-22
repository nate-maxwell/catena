from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.clouds import CloudsProcessor
from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.generate.perlin_noise import PerlinNoiseProcessor
from catena.nodes.image.levels import LevelsProcessor
from catena.nodes.image.warp import WarpProcessor
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.transform.rotate_scale import RotateScaleProcessor


class GrungeTwoProcessor(ProcessorNode):
    """A headless processor that generates a grunge noise map."""

    def __init__(
        self,
        balance: float = 0.5,
        contrast: float = 1.0,
        disorder: float = 0.5,
        invert: bool = False,
        seed: int = 0,
    ) -> None:
        super().__init__()
        self.balance = balance
        self.contrast = contrast
        self.disorder = disorder
        self.invert = invert
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]] | None = None
    ) -> Optional[numpy.ndarray]:
        self.seed = self.seed if not self.seed is None else 1234

        perlin_img = PerlinNoiseProcessor(256, 5, self.seed).process()
        clouds_img = CloudsProcessor(seed=self.seed).process()

        levels = LevelsProcessor(output_low=53)
        levels_img = levels.process({"Input": perlin_img})

        warp1 = WarpProcessor(100)
        warp1_img = warp1.process({"Input": levels_img, "Displacement": clouds_img})

        warp2 = WarpProcessor(200)
        warp2_img = warp2.process({"Input": warp1_img, "Displacement": clouds_img})

        rotate = RotateScaleProcessor()
        rotate.angle = 90

        return rotate.process({"Input": warp2_img})


class GrungeTwoNode(GeneratorNode):
    """A node that generates a grunge noise map."""

    def __init__(self) -> None:
        self._processor = GrungeTwoProcessor()
        super().__init__(title="Grunge 2")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

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
        self._processor.seed = self.get_field_value("seed")
        return self._processor.process(inputs)
