from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType
from scipy.spatial import cKDTree

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode


class CellsProcessor(ProcessorNode):
    """A headless processor that generates cellular (Worley) noise."""

    def __init__(
        self,
        cells: int = 16,
        seed: int = 0,
        invert: bool = False,
    ) -> None:
        super().__init__()
        self.cells = cells
        self.seed = seed
        self.invert = invert

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate cellular (Worley) noise using KD-tree nearest-neighbour lookup.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 cellular noise image of shape
                (512, 512, 3) with values in [0, 1].
        """
        width, height = 512, 512
        rng = numpy.random.default_rng(self.seed)

        points = rng.random((self.cells, 2))
        points[:, 0] *= width
        points[:, 1] *= height

        offsets = numpy.array(
            [
                (-width, -height),
                (0, -height),
                (width, -height),
                (-width, 0),
                (0, 0),
                (width, 0),
                (-width, height),
                (0, height),
                (width, height),
            ],
            dtype=numpy.float32,
        )

        all_points = (points[:, None, :] + offsets[None, :, :]).reshape(-1, 2)

        tree = cKDTree(all_points)

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
        query_points = numpy.stack([x_idx.ravel(), y_idx.ravel()], axis=1)

        distances, _ = tree.query(query_points)

        min_dist = distances.reshape(height, width).astype(numpy.float32)
        min_dist /= min_dist.max()

        if self.invert:
            min_dist = 1.0 - min_dist

        return numpy.repeat(min_dist[:, :, None], 3, axis=2).astype(numpy.float32)


class CellsNode(GeneratorNode):
    """A node that generates cellular (Worley) noise."""

    def __init__(self) -> None:
        self._processor = CellsProcessor()
        super().__init__(title="Cells")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="cells",
                label="Cells",
                field_type=FieldType.INT,
                default=16,
                min_value=2,
                max_value=1024,
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
        self.add_field(
            FieldDefinition(
                name="invert",
                label="Invert",
                field_type=FieldType.BOOL,
                default=False,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.cells = self.get_field_value("cells")
        self._processor.seed = self.get_field_value("seed")
        self._processor.invert = self.get_field_value("invert")
        return self._processor.process(inputs)
