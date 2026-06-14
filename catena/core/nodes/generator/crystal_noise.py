from typing import Optional

import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType
from scipy.spatial import cKDTree

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.generator import IMAGE_NODE_COLOR


class CrystalNoiseNode(CatenaNode):
    """A node that generates crystal/Voronoi facet noise."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Crystal", body_height=80)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="cells",
                label="Cells",
                field_type=FieldType.INT,
                default=16,
                min_value=2,
                max_value=128,
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
        cells = self.get_field_value("cells")
        seed = self.get_field_value("seed")

        width, height = 512, 512
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

        all_points = (points[:, None, :] + offsets[None, :, :]).reshape(-1, 2)
        all_values = numpy.tile(values, len(offsets))

        tree = cKDTree(all_points)

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
        query_points = numpy.stack([x_idx.ravel(), y_idx.ravel()], axis=1)

        _, indices = tree.query(query_points)

        nearest = all_values[indices].reshape(height, width)

        result = numpy.repeat(nearest[:, :, None], 3, axis=2).astype(numpy.float32)
        return result
