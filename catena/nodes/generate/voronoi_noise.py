from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType
from scipy.spatial import cKDTree

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences


class VoronoiNoiseProcessor(ProcessorNode):
    """A headless processor that generates crystal/Voronoi facet noise."""

    def __init__(self, cells: int = 16, seed: int = 0) -> None:
        super().__init__()
        self.cells = cells
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]] | None = None
    ) -> Optional[numpy.ndarray]:
        """
        Generate crystal/Voronoi facet noise using KD-tree nearest-neighbor lookup.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 Voronoi noise modifier of shape
                (width, height, 3) with values in [0, 1].
        """
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width
        rng = numpy.random.default_rng(self.seed)

        points = rng.random((self.cells, 2))
        points[:, 0] *= width
        points[:, 1] *= height

        values = rng.random(self.cells).astype(numpy.float32)

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

        all_points = []
        all_indices = []
        for i, offset in enumerate(offsets):
            all_points.append(points + offset)
            all_indices.append(numpy.arange(self.cells))

        all_points = numpy.concatenate(all_points, axis=0)
        all_indices = numpy.concatenate(all_indices, axis=0)

        tree = cKDTree(all_points)

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
        query_points = numpy.stack([x_idx.ravel(), y_idx.ravel()], axis=1)

        _, indices = tree.query(query_points)

        nearest = values[all_indices[indices]].reshape(height, width)

        return numpy.repeat(nearest[:, :, None], 3, axis=2).astype(numpy.float32)


class VoronoiNoiseNode(GeneratorNode):
    """A node that generates crystal/Voronoi facet noise."""

    def __init__(self) -> None:
        self._processor = VoronoiNoiseProcessor()
        super().__init__(title="Voronoi")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="cells",
                label="Cells",
                field_type=FieldType.INT,
                default=16,
                min_value=2,
                max_value=4096,
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
        self._processor.cells = self.get_field_value("cells")
        self._processor.seed = self.get_field_value("seed")
        return self._processor.process(inputs)
