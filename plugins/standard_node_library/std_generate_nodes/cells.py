from typing import Optional

import numpy
from scipy.spatial import cKDTree

from catena import api
from std_generate_nodes.generator import GeneratorNode


class CellsNode(GeneratorNode):
    """A node that generates cellular (Worley) noise."""

    def __init__(self) -> None:
        super().__init__(title="Cells")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="cells",
                label="Cells",
                field_type=api.FieldType.INT,
                default=16,
                min_value=2,
                max_value=1024,
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
        self.add_field(
            api.FieldDefinition(
                name="invert",
                label="Invert",
                field_type=api.FieldType.BOOL,
                default=False,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate cellular (Worley) noise using KD-tree nearest-neighbor lookup.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 cellular noise modifier of shape
                (width, height, 3) with values in [0, 1].
        """
        cells = self.get_field_value("cells")
        invert = self.get_field_value("invert")
        seed = self.get_field_value("seed")
        seed = int(seed * 255) if isinstance(seed, float) else int(seed)
        width, height = api.get_texture_resolution()
        rng = numpy.random.default_rng(seed)

        points = rng.random((cells, 2))
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

        if invert:
            min_dist = 1.0 - min_dist

        return numpy.repeat(min_dist[:, :, None], 4, axis=2).astype(numpy.float32)
