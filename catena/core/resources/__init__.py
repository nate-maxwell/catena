from pathlib import Path

_resources_dir = Path(__file__).parent

# Client

ICON_CATENA = _resources_dir / "ICON_Catena.png"


# Texture

TEXTURE_DIR = _resources_dir / "texture"

SHD_DEFAULT_AO = TEXTURE_DIR / "T_Default_AO.png"
SHD_DEFAULT_BC = TEXTURE_DIR / "T_Default_BC.png"
SHD_DEFAULT_H = TEXTURE_DIR / "T_Default_H.png"
SHD_DEFAULT_M = TEXTURE_DIR / "T_Default_M.png"
SHD_DEFAULT_N = TEXTURE_DIR / "T_Default_N.png"
SHD_DEFAULT_R = TEXTURE_DIR / "T_Default_R.png"

# Geometry

GEO_DIR = _resources_dir / "geo"

GEO_SHADER_BALL = _resources_dir / "shaderBall.obj"
GEO_CUBE = _resources_dir / "SM_Cube.obj"
GEO_CYLINDER = _resources_dir / "SM_Cylinder.obj"
GEO_PLANE = _resources_dir / "SM_Plane.obj"
