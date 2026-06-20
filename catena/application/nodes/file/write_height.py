import broker
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType

from catena.application import namespace
from catena.application import texture
from catena.application.nodes.base import CatenaNode
from catena.application.nodes.file import IMAGE_NODE_COLOR
from catena.application.nodes.file.write import WriteNode


class HeightNode(WriteNode):

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Height", texture_type=texture.TextureType.HEIGHT)

    def _build(self) -> None:
        super()._build()

        self.add_field(
            FieldDefinition(
                name="displacement",
                label="Displacement",
                field_type=FieldType.INT,
                default=0,
                min_value=0,
                max_value=100,
            )
        )

    def _on_field_changed(self, node: CatenaNode) -> None:
        super()._on_field_changed(node)
        val = self.get_field_value("displacement")
        broker.emit(namespace.NODE_DISPLACEMENT_UPDATED, scale=val)
