from catena import texture
from catena.nodes.file import IMAGE_NODE_COLOR
from catena.nodes.file.write import WriteNode


class AlbedoNode(WriteNode):

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Albedo", texture_type=texture.TextureType.ALBEDO)
