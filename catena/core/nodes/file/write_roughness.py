from catena.core import texture
from catena.core.nodes.file import IMAGE_NODE_COLOR
from catena.core.nodes.file.write import WriteNode


class RoughnessNode(WriteNode):

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Roughness", texture_type=texture.TextureType.ROUGHNESS)
