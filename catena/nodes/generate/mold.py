from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences

IMAGE_NODE_COLOR: tuple[int, int, int] = (80, 120, 160)


class MoldProcessor(ProcessorNode):
    """A headless processor that generates a moisture/wetness map."""

    def __init__(
        self,
        num_drops: int = 180,
        drop_scale: float = 0.5,
        grunge: float = 0.55,
        seed: int = 0,
    ) -> None:
        super().__init__()
        self.num_drops = num_drops
        self.drop_scale = drop_scale
        self.grunge = grunge
        self.seed = seed

    def _value_noise(
        self,
        height: int,
        width: int,
        cell_size: float,
        rng: numpy.random.Generator,
    ) -> numpy.ndarray:
        """
        Generate smooth value noise by resizing a random lattice.

        Args:
            height (int): Output modifier height in pixels.
            width (int): Output modifier width in pixels.
            cell_size (float): Size of each noise cell in pixels.
            rng (numpy.random.Generator): Seeded random generator.
        Returns:
            numpy.ndarray: A float32 array of shape (height, width) with
                values in [0, 1].
        """
        lh = max(2, int(height / cell_size))
        lw = max(2, int(width / cell_size))
        lattice = rng.random((lh, lw)).astype(numpy.float32)
        return cv2.resize(lattice, (width, height), interpolation=cv2.INTER_CUBIC)

    def _render_drop_layer(
        self,
        height: int,
        width: int,
        centers_y: list[int],
        centers_x: list[int],
        radii: list[float],
        blur_frac: float,
    ) -> numpy.ndarray:
        """
        Render a set of drops into a float canvas using cv2.circle for all
        drops at once, then apply a single Gaussian blur for soft edge falloff.

        Args:
            height (int): Canvas height in pixels.
            width (int): Canvas width in pixels.
            centers_y (list[int]): Drop center Y coordinates.
            centers_x (list[int]): Drop center X coordinates.
            radii (list[float]): Drop radii in pixels.
            blur_frac (float): Blur sigma as a fraction of the median radius.
        Returns:
            numpy.ndarray: A float32 canvas of shape (height, width) with
                values in [0, 1].
        """
        canvas = numpy.zeros((height, width), dtype=numpy.float32)
        for cy, cx, r in zip(centers_y, centers_x, radii):
            cv2.circle(canvas, (cx, cy), max(1, int(r)), 1.0, -1)
        med_r = float(numpy.median(radii))
        k = max(3, int(med_r * blur_frac * 2) | 1)
        return cv2.GaussianBlur(canvas, (k, k), med_r * blur_frac)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a moisture map by scattering soft elliptical drops in three
        size classes near cluster centers, rendered via cv2.circle and a
        per-class Gaussian blur for performance. A low-frequency noise base
        provides broad tonal variation, and a grunge layer adds fine surface
        speckle.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 BGR modifier of shape (H, W, 3)
                with values in [0, 1].
        """
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width
        seed = int(self.seed)

        rng = numpy.random.default_rng(int(seed))
        rng_base = numpy.random.default_rng(seed + 11)
        rng_warp = numpy.random.default_rng(seed + 99)
        rng_grng = numpy.random.default_rng(seed + 3)

        # Large-scale uneven base: smooth low-frequency noise in mid-tone range
        # so the surface reads as damp without pure black or white.
        base = self._value_noise(height, width, height * 0.30, rng_base)
        base = cv2.GaussianBlur(base, (31, 31), 0)
        base -= base.min()
        if base.max() > 0.0:
            base /= base.max()
        result = (0.35 + base * 0.37).astype(numpy.float32)

        # Cluster centers: drops congregate in wet zones rather than being
        # uniformly scattered, matching how moisture pools on surfaces.
        n_clusters = max(4, self.num_drops // 22)
        cluster_y = rng.uniform(0, height, n_clusters)
        cluster_x = rng.uniform(0, width, n_clusters)
        cluster_r = rng.uniform(height * 0.10, height * 0.28, n_clusters)

        # Domain warp: displaces each drop center for organic irregularity.
        warp_y = (
            (self._value_noise(height, width, height * 0.12, rng_warp) - 0.5)
            * height
            * 0.035
        )
        warp_x = (
            (self._value_noise(height, width, height * 0.12, rng_warp) - 0.5)
            * height
            * 0.035
        )

        for r_lo, r_hi, count_frac, strength, blur_frac in [
            (0.028, 0.080, 0.15, 0.48, 0.50),
            (0.009, 0.030, 0.40, 0.35, 0.60),
            (0.002, 0.010, 0.45, 0.22, 0.80),
        ]:
            n = int(self.num_drops * count_frac)
            cys: list[int] = []
            cxs: list[int] = []
            rs: list[float] = []
            for _ in range(n):
                ci = rng.integers(0, n_clusters)
                ang = rng.uniform(0, 2.0 * numpy.pi)
                d = rng.uniform(0, cluster_r[ci])
                cy = int(numpy.clip(cluster_y[ci] + numpy.sin(ang) * d, 0, height - 1))
                cx = int(numpy.clip(cluster_x[ci] + numpy.cos(ang) * d, 0, width - 1))
                cy = int(numpy.clip(cy + warp_y[cy, cx], 0, height - 1))
                cx = int(numpy.clip(cx + warp_x[cy, cx], 0, width - 1))
                r = rng.uniform(r_lo, r_hi) * height * self.drop_scale
                if r < 1.5:
                    continue
                cys.append(cy)
                cxs.append(cx)
                rs.append(r)

            if not cys:
                continue

            layer = self._render_drop_layer(height, width, cys, cxs, rs, blur_frac)
            result -= layer * strength

        # Grunge: two-frequency speckle layer crushed by power curve to add
        # fine gritty variation across the whole surface.
        speck = (
            self._value_noise(height, width, height * 0.05, rng_grng) * 0.55
            + self._value_noise(height, width, height * 0.02, rng_grng) * 0.45
        )
        speck -= speck.min()
        if speck.max() > 0.0:
            speck /= speck.max()
        speck = numpy.power(speck, 2.2 - self.grunge * 1.2)
        result -= speck * self.grunge * 0.15

        result = numpy.clip(result, 0.0, 1.0)
        return numpy.repeat(result[:, :, None], 3, axis=2).astype(numpy.float32)


class MoldNode(GeneratorNode):
    """A node that generates a procedural moisture/wetness map."""

    def __init__(self) -> None:
        self._processor = MoldProcessor()
        super().__init__(title="Mold")

    def _get_node_color(self) -> tuple[int, int, int]:
        return IMAGE_NODE_COLOR

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="num_drops",
                label="Drops",
                field_type=FieldType.INT,
                default=180,
                min_value=10,
                max_value=999999,
            )
        )
        self.add_field(
            FieldDefinition(
                name="drop_scale",
                label="Drop Scale",
                field_type=FieldType.FLOAT,
                default=0.5,
                min_value=0.1,
                max_value=2.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="grunge",
                label="Grunge",
                field_type=FieldType.FLOAT,
                default=0.55,
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
        self._processor.num_drops = self.get_field_value("num_drops")
        self._processor.drop_scale = self.get_field_value("drop_scale")
        self._processor.grunge = self.get_field_value("grunge")
        seed = self.get_field_value("seed")
        self._processor.seed = int(seed * 255) if isinstance(seed, float) else int(seed)
        return self._processor.process(inputs)
