from catena import texture
from catena.nodes.file import IMAGE_NODE_COLOR
from catena.nodes.file.write import WriteNode


class AmbientOcclusionNode(WriteNode):

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="AO", texture_type=texture.TextureType.AO)
