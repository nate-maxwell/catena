import broker
from core_utils import regex
from PySide6TK import QtCore
from PySide6TK import QtWidgets
from PySide6TK.Nodes import GraphView
from PySide6TK.Nodes import Port
from PySide6TK.Nodes import Wire

from catena.application import namespace
from catena.application.nodes.base import CatenaNode
from catena.application.nodes.comment import CatenaCommentBox
from catena.application.nodes.convert.append import AppendNode
from catena.application.nodes.convert.height_to_ao import HeightToAONode
from catena.application.nodes.convert.height_to_normal import HeightToNormalNode
from catena.application.nodes.convert.split import SplitNode
from catena.application.nodes.file.read import ReadNode
from catena.application.nodes.file.write import WriteNode
from catena.application.nodes.file.write_albedo import AlbedoNode
from catena.application.nodes.file.write_ambient_occlusion import AONode
from catena.application.nodes.file.write_height import HeightNode
from catena.application.nodes.file.write_metallic import MetallicNode
from catena.application.nodes.file.write_normal import NormalNode
from catena.application.nodes.file.write_roughness import RoughnessNode
from catena.application.nodes.generate.blue_noise import BlueNoiseNode
from catena.application.nodes.generate.bnw_spots import BNWSpotsNode
from catena.application.nodes.generate.cells import CellsNode
from catena.application.nodes.generate.clouds import CloudsNode
from catena.application.nodes.generate.voronoi_noise import VoronoiNoiseNode
from catena.application.nodes.generate.gradient import GradientNode
from catena.application.nodes.generate.perlin_noise import PerlinNoiseNode
from catena.application.nodes.generate.polygon import PolygonNode
from catena.application.nodes.generate.shape import ShapeNode
from catena.application.nodes.generate.white_noise import WhiteNoiseNode
from catena.application.nodes.image.bevel import BevelNode
from catena.application.nodes.image.blur import BlurNode
from catena.application.nodes.image.color import ColorNode
from catena.application.nodes.image.contrast import ContrastNode
from catena.application.nodes.image.hsv import HSVNode
from catena.application.nodes.image.invert import InvertNode
from catena.application.nodes.image.levels import LevelsNode
from catena.application.nodes.image.normalize import NormalizeNode
from catena.application.nodes.image.overlay import OverlayNode
from catena.application.nodes.image.sharpen import SharpenNode
from catena.application.nodes.image.slope_blur import SlopeBlurNode
from catena.application.nodes.image.threshold import ThresholdNode
from catena.application.nodes.image.warp import WarpNode
from catena.application.nodes.math.add import AddNode
from catena.application.nodes.math.arctan import ArctangentNode
from catena.application.nodes.math.cosin import CosineNode
from catena.application.nodes.math.divide import DivideNode
from catena.application.nodes.math.max import MaxNode
from catena.application.nodes.math.min import MinNode
from catena.application.nodes.math.multiply import MultiplyNode
from catena.application.nodes.math.screen import ScreenNode
from catena.application.nodes.math.sin import SinNode
from catena.application.nodes.math.subtract import SubtractNode
from catena.application.nodes.math.tan import TangentNode
from catena.application.nodes.misc.reroute import RerouteNode
from catena.application.nodes.transform.flip import FlipNode
from catena.application.nodes.transform.offset import OffsetNode
from catena.application.nodes.transform.rotate import RotateNode
from catena.application.nodes.transform.scatter import ScatterNode
from catena.application.nodes.transform.tile import TileNode


class CatenaGraphView(GraphView):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.comment_type = CatenaCommentBox
        self._register_nodes()

    def add_comment(
        self, x: float, y: float, label: str = "Comment"
    ) -> CatenaCommentBox:
        """
        Add a comment box to the scene at the given scene coordinates.

        Args:
            x (float): Scene x position.
            y (float): Scene y position.
            label (str): Initial comment label.
        Returns:
            CommentBox: The created comment box.
        """
        box = CatenaCommentBox(label)
        self._node_refs.append(box)
        self.scene.addItem(box)
        box.setPos(x, y)
        return box

    def connect_ports_internal(self, source: Port, target: Port) -> Wire:
        wire = super().connect_ports_internal(source, target)

        self._invalidate_and_refresh_from_port(target)
        self._refresh_active_preview()

        return wire

    def destroy_wire(self, wire: Wire) -> None:
        target = wire.target

        super().destroy_wire(wire)

        if target is not None:
            self._invalidate_and_refresh_from_port(target)

        self._refresh_active_preview()

    @staticmethod
    def _invalidate_and_refresh_from_port(port: Port) -> None:
        node = port.parentItem()
        if not isinstance(node, CatenaNode):
            return

        node._invalidate_downstream()
        node._refresh_downstream_write_nodes()

    @staticmethod
    def _refresh_downstream_write_nodes(node: CatenaNode) -> None:
        visited: set[CatenaNode] = set()
        stack: list[CatenaNode] = [node]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)

            if isinstance(current, WriteNode):
                current._emit_preview_update()

            for output_port in current.output_ports():
                for wire in output_port.wires:
                    target_node = wire.target.parentItem()
                    if isinstance(target_node, CatenaNode):
                        stack.append(target_node)

    @staticmethod
    def _refresh_active_preview() -> None:
        node = CatenaNode.active_preview_node
        if node is not None:
            broker.emit(namespace.NODE_PREVIEW, image=node.evaluate())

    def _on_context_menu(self, viewport_pos: QtCore.QPoint) -> None:
        """Overridden from parent to convert names from 'BevelNode' to 'Bevel'."""
        item = self.itemAt(viewport_pos)
        if item is not None:
            return

        scene_pos = self.mapToScene(viewport_pos)
        menu = QtWidgets.QMenu(self)

        comment_action = menu.addAction("Add Comment")
        comment_action.setData(("comment", scene_pos))
        menu.addSeparator()

        for category, node_types in sorted(self.node_registry.items()):
            submenu = menu.addMenu(category)
            for node_type in node_types:
                snake_case = regex.pascal_to_snake(node_type.__name__)
                name = snake_case.replace("_", " ").replace("node", "")
                entry = name.title()
                action = submenu.addAction(entry)
                action.setData(("node", node_type, scene_pos))

        chosen = menu.exec(self.viewport().mapToGlobal(viewport_pos))
        if chosen is None:
            return

        data = chosen.data()
        if data[0] == "comment":
            self.add_comment(data[1].x(), data[1].y())
        elif data[0] == "node":
            node = data[1]()
            self.add_node(node, data[2].x(), data[2].y())

    def _register_nodes(self) -> None:
        self._register_convert_nodes()
        self._register_create_nodes()
        self._register_image_nodes()
        self._register_transform_nodes()
        self._register_math_nodes()
        self._register_misc_nodes()
        self._register_generator_nodes()

    def _register_convert_nodes(self) -> None:
        self.register_node("Convert", AppendNode)
        self.register_node("Convert", HeightToAONode)
        self.register_node("Convert", HeightToNormalNode)
        self.register_node("Convert", SplitNode)

    def _register_create_nodes(self) -> None:
        self.register_node("Create", ReadNode)
        self.register_node("Create", AlbedoNode)
        self.register_node("Create", AONode)
        self.register_node("Create", HeightNode)
        self.register_node("Create", MetallicNode)
        self.register_node("Create", NormalNode)
        self.register_node("Create", RoughnessNode)

    def _register_image_nodes(self) -> None:
        self.register_node("Image", BevelNode)
        self.register_node("Image", BlurNode)
        self.register_node("Image", ColorNode)
        self.register_node("Image", ContrastNode)
        self.register_node("Image", HSVNode)
        self.register_node("Image", InvertNode)
        self.register_node("Image", LevelsNode)
        self.register_node("Image", NormalizeNode)
        self.register_node("Image", OverlayNode)
        self.register_node("Image", SharpenNode)
        self.register_node("Image", SlopeBlurNode)
        self.register_node("Image", ThresholdNode)
        self.register_node("Image", WarpNode)

    def _register_transform_nodes(self) -> None:
        self.register_node("Transform", FlipNode)
        self.register_node("Transform", OffsetNode)
        self.register_node("Transform", RotateNode)
        self.register_node("Transform", ScatterNode)
        self.register_node("Transform", TileNode)

    def _register_math_nodes(self) -> None:
        self.register_node("Math", AddNode)
        self.register_node("Math", ArctangentNode)
        self.register_node("Math", CosineNode)
        self.register_node("Math", DivideNode)
        self.register_node("Math", MaxNode)
        self.register_node("Math", MinNode)
        self.register_node("Math", MultiplyNode)
        self.register_node("Math", ScreenNode)
        self.register_node("Math", SinNode)
        self.register_node("Math", SubtractNode)
        self.register_node("Math", TangentNode)

    def _register_misc_nodes(self) -> None:
        self.register_node("Misc", RerouteNode)

    def _register_generator_nodes(self) -> None:
        self.register_node("Generator", BlueNoiseNode)
        self.register_node("Generator", BNWSpotsNode)
        self.register_node("Generator", CellsNode)
        self.register_node("Generator", CloudsNode)
        self.register_node("Generator", VoronoiNoiseNode)
        self.register_node("Generator", GradientNode)
        self.register_node("Generator", PerlinNoiseNode)
        self.register_node("Generator", PolygonNode)
        self.register_node("Generator", ShapeNode)
        self.register_node("Generator", WhiteNoiseNode)
