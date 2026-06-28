from typing import Optional

import numpy
from scipy.spatial import cKDTree

from catena import api
from std_generate_nodes.generator import GeneratorNode


class VoronoiNoiseNode(GeneratorNode):
    """A node that generates crystal/Voronoi facet noise."""

    def __init__(self) -> None:
        super().__init__(title="Voronoi")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="cells",
                label="Cells",
                field_type=api.FieldType.INT,
                default=16,
                min_value=2,
                max_value=4096,
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
        Generate crystal/Voronoi facet noise using KD-tree nearest-neighbor lookup.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 Voronoi noise modifier of shape
                (width, height, 3) with values in [0, 1].
        """
        cells = self.get_field_value("cells")

        seed = self.get_field_value("seed")
        seed = int(seed * 255) if isinstance(seed, float) else int(seed)

        width, height = api.get_texture_resolution()
        rng = numpy.random.default_rng(seed)

        points = rng.random((cells, 2))
        points[:, 0] *= width
        points[:, 1] *= height

        values = rng.random(cells).astype(numpy.float32)

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
            all_indices.append(numpy.arange(cells))

        all_points = numpy.concatenate(all_points, axis=0)
        all_indices = numpy.concatenate(all_indices, axis=0)

        tree = cKDTree(all_points)

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
        query_points = numpy.stack([x_idx.ravel(), y_idx.ravel()], axis=1)

        _, indices = tree.query(query_points)

        nearest = values[all_indices[indices]].reshape(height, width)

        return numpy.repeat(nearest[:, :, None], 4, axis=2).astype(numpy.float32)
