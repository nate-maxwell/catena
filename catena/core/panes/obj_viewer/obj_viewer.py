import ctypes
import math
from pathlib import Path
from typing import Optional

import OpenGL.GL as gl
import imageio.v3 as imageio
import numpy
from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtOpenGLWidgets
from PySide6TK import QtWidgets

from catena.core import resources
from catena.core.panes.obj_viewer import matrix

SHADER_DIR = Path(__file__).parent


def load_obj(path: Path) -> tuple[list[float], list[int]]:
    """
    Load interleaved vertex data and triangle indices from an OBJ file.

    Parses positions, texture coordinates, and normals. If the file contains no
    normals, smooth per-vertex normals are computed from face geometry. Output
    vertices are interleaved as position (3), normal (3), texcoord (2) per vertex,
    with one unique vertex per distinct position/normal/texcoord combination.

    Args:
        path (Path): Path to the .obj file.
    Returns:
        tuple[list[float], list[int]]: Flat interleaved vertex data (8 floats
            per vertex) and flat triangle index array.
    """
    raw_positions: list[tuple[float, float, float]] = []
    raw_texcoords: list[tuple[float, float]] = []
    raw_normals: list[tuple[float, float, float]] = []
    raw_faces: list[list[tuple[int, int, int]]] = []

    with open(path, "r", encoding="utf-8") as obj_file:
        for line in obj_file:
            tokens = line.split()
            if not tokens:
                continue
            if tokens[0] == "v":
                raw_positions.append(
                    (float(tokens[1]), float(tokens[2]), float(tokens[3]))
                )
            elif tokens[0] == "vt":
                raw_texcoords.append((float(tokens[1]), float(tokens[2])))
            elif tokens[0] == "vn":
                raw_normals.append(
                    (float(tokens[1]), float(tokens[2]), float(tokens[3]))
                )
            elif tokens[0] == "f":
                face: list[tuple[int, int, int]] = []
                for token in tokens[1:]:
                    parts = token.split("/")
                    position_index = int(parts[0]) - 1
                    texcoord_index = (
                        int(parts[1]) - 1 if len(parts) > 1 and parts[1] else -1
                    )
                    normal_index = (
                        int(parts[2]) - 1 if len(parts) > 2 and parts[2] else -1
                    )
                    face.append((position_index, texcoord_index, normal_index))
                raw_faces.append(face)

    if not raw_normals:
        computed_normals = [[0.0, 0.0, 0.0] for _ in raw_positions]
        for face in raw_faces:
            for i in range(1, len(face) - 1):
                i0, i1, i2 = face[0][0], face[i][0], face[i + 1][0]
                v0, v1, v2 = raw_positions[i0], raw_positions[i1], raw_positions[i2]
                ux, uy, uz = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
                vx, vy, vz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
                nx = uy * vz - uz * vy
                ny = uz * vx - ux * vz
                nz = ux * vy - uy * vx
                for idx in (i0, i1, i2):
                    computed_normals[idx][0] += nx
                    computed_normals[idx][1] += ny
                    computed_normals[idx][2] += nz
        for normal in computed_normals:
            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
            if length > 0.0:
                normal[0] /= length
                normal[1] /= length
                normal[2] /= length
        raw_normals = [tuple(normal) for normal in computed_normals]
        use_position_index_as_normal = True
    else:
        use_position_index_as_normal = False

    vertex_cache: dict[tuple[int, int, int], int] = {}
    interleaved: list[float] = []
    indices: list[int] = []

    for face in raw_faces:
        resolved: list[int] = []
        for position_index, texcoord_index, normal_index in face:
            effective_normal_index = (
                position_index if use_position_index_as_normal else normal_index
            )
            key = (position_index, texcoord_index, effective_normal_index)
            if key not in vertex_cache:
                vertex_cache[key] = len(interleaved) // 8
                px, py, pz = raw_positions[position_index]
                if effective_normal_index >= 0:
                    nx, ny, nz = raw_normals[effective_normal_index]
                else:
                    nx, ny, nz = 0.0, 0.0, 1.0
                if texcoord_index >= 0:
                    tu, tv = raw_texcoords[texcoord_index]
                else:
                    tu, tv = 0.0, 0.0
                interleaved.extend((px, py, pz, nx, ny, nz, tu, tv))
            resolved.append(vertex_cache[key])

        for i in range(1, len(resolved) - 1):
            indices.append(resolved[0])
            indices.append(resolved[i])
            indices.append(resolved[i + 1])

    return interleaved, indices


def compute_tangents(interleaved: list[float], indices: list[int]) -> list[float]:
    """
    Compute per-vertex tangents and append them to interleaved vertex data.

    Args:
        interleaved (list[float]): Flat interleaved vertex data (8 floats per
            vertex: position, normal, texcoord).
        indices (list[int]): Flat triangle index array.
    Returns:
        list[float]: Flat interleaved vertex data with tangents appended (11
            floats per vertex: position, normal, texcoord, tangent).
    """
    vertex_count = len(interleaved) // 8
    tangents = [[0.0, 0.0, 0.0] for _ in range(vertex_count)]

    for i in range(0, len(indices), 3):
        i0, i1, i2 = indices[i], indices[i + 1], indices[i + 2]

        p0 = interleaved[i0 * 8 : i0 * 8 + 3]
        p1 = interleaved[i1 * 8 : i1 * 8 + 3]
        p2 = interleaved[i2 * 8 : i2 * 8 + 3]

        uv0 = interleaved[i0 * 8 + 6 : i0 * 8 + 8]
        uv1 = interleaved[i1 * 8 + 6 : i1 * 8 + 8]
        uv2 = interleaved[i2 * 8 + 6 : i2 * 8 + 8]

        edge1 = [p1[j] - p0[j] for j in range(3)]
        edge2 = [p2[j] - p0[j] for j in range(3)]
        delta_uv1 = [uv1[j] - uv0[j] for j in range(2)]
        delta_uv2 = [uv2[j] - uv0[j] for j in range(2)]

        denom = delta_uv1[0] * delta_uv2[1] - delta_uv2[0] * delta_uv1[1]
        if abs(denom) < 1e-12:
            continue
        inv_denom = 1.0 / denom

        tangent = [
            inv_denom * (delta_uv2[1] * edge1[j] - delta_uv1[1] * edge2[j])
            for j in range(3)
        ]

        for idx in (i0, i1, i2):
            tangents[idx][0] += tangent[0]
            tangents[idx][1] += tangent[1]
            tangents[idx][2] += tangent[2]

    extended: list[float] = []
    for vertex_index in range(vertex_count):
        vertex_data = interleaved[vertex_index * 8 : vertex_index * 8 + 8]
        tangent = tangents[vertex_index]
        length = math.sqrt(tangent[0] ** 2 + tangent[1] ** 2 + tangent[2] ** 2)
        if length > 0.0:
            tangent = [component / length for component in tangent]
        else:
            tangent = [1.0, 0.0, 0.0]
        extended.extend(vertex_data)
        extended.extend(tangent)

    return extended


def compile_shader_program(vertex_path: Path, fragment_path: Path) -> int:
    """
    Compile and link a GLSL shader program from vertex and fragment source files.

    Args:
        vertex_path (Path): Path to the vertex shader source file.
        fragment_path (Path): Path to the fragment shader source file.
    Returns:
        int: The linked shader program's OpenGL handle.
    """
    vertex_source = vertex_path.read_text(encoding="utf-8")
    fragment_source = fragment_path.read_text(encoding="utf-8")

    vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vertex_shader, vertex_source)
    gl.glCompileShader(vertex_shader)
    if not gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS):
        raise RuntimeError(gl.glGetShaderInfoLog(vertex_shader).decode("utf-8"))

    fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    gl.glShaderSource(fragment_shader, fragment_source)
    gl.glCompileShader(fragment_shader)
    if not gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS):
        raise RuntimeError(gl.glGetShaderInfoLog(fragment_shader).decode("utf-8"))

    program = gl.glCreateProgram()
    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)
    gl.glLinkProgram(program)
    if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
        raise RuntimeError(gl.glGetProgramInfoLog(program).decode("utf-8"))

    gl.glDeleteShader(vertex_shader)
    gl.glDeleteShader(fragment_shader)
    return program


def load_texture(path: Path, srgb: bool) -> int:
    """Load an image file into an OpenGL 2D texture.

    Args:
        path (Path): Path to the image file.
        srgb (bool): If True, the texture is stored in an sRGB internal format
            (for albedo/color data). If False, a linear format is used (for
            metallic-roughness, normal, etc. data maps).

    Returns:
        int: The OpenGL texture handle.
    """
    image = imageio.imread(path)
    return create_texture_from_array(image, srgb)


def to_uint8(image: numpy.ndarray) -> numpy.ndarray:
    """
    Convert an image array to uint8, scaling floating-point data from 0.0-1.0 to 0-255.

    Args:
        image (numpy.ndarray): Image data, either uint8 or floating-point in range 0.0-1.0.
    Returns:
        numpy.ndarray: Image data as uint8.
    """
    if numpy.issubdtype(image.dtype, numpy.floating):
        image = numpy.clip(image, 0.0, 1.0) * 255.0
        return image.astype(numpy.uint8)
    return image.astype(numpy.uint8)


def create_texture_from_array(image: numpy.ndarray, srgb: bool) -> int:
    """
    Upload an image array into an OpenGL 2D texture.

    Args:
        image (numpy.ndarray): Image data as a 2D (grayscale) or 3D (RGB/RGBA)
            array, either uint8 in range 0-255 or floating-point in range 0.0-1.0.
        srgb (bool): If True, the texture is stored in an sRGB internal format
            (for albedo/color data). If False, a linear format is used (for
            metallic-roughness, normal, etc. data maps).
    Returns:
        int: The OpenGL texture handle.
    """
    image = to_uint8(image)

    if image.ndim == 2:
        image = numpy.stack([image] * 3, axis=-1)
    if image.shape[2] == 3:
        alpha = numpy.full((image.shape[0], image.shape[1], 1), 255, dtype=numpy.uint8)
        image = numpy.concatenate([image, alpha], axis=-1)

    image = numpy.flipud(image)
    image = numpy.ascontiguousarray(image)

    internal_format = gl.GL_SRGB8_ALPHA8 if srgb else gl.GL_RGBA8

    texture_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        internal_format,
        image.shape[1],
        image.shape[0],
        0,
        gl.GL_RGBA,
        gl.GL_UNSIGNED_BYTE,
        image,
    )
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
    gl.glTexParameteri(
        gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR
    )
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

    return texture_id


def create_solid_texture(rgba: tuple[int, int, int, int]) -> int:
    """
    Create a 1x1 OpenGL 2D texture filled with a constant color.

    Args:
        rgba (tuple[int, int, int, int]): Red, green, blue, and alpha values
            in the range 0-255.
    Returns:
        int: The OpenGL texture handle.
    """
    image = numpy.array([[rgba]], dtype=numpy.uint8)

    texture_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGBA8,
        1,
        1,
        0,
        gl.GL_RGBA,
        gl.GL_UNSIGNED_BYTE,
        image,
    )
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    return texture_id


class ObjViewer(QtOpenGLWidgets.QOpenGLWidget):
    """An OpenGL widget that displays a PBR-shaded OBJ mesh with mouse-based orbit controls."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        # object
        self._obj_path: Path = resources.OBJ_SHADER_BALL
        # textures
        self._albedo_path: Path = resources.SHD_DEFAULT_BC
        self._metallic_path: Path = resources.SHD_DEFAULT_M
        self._roughness_path: Path = resources.SHD_DEFAULT_R
        self._normal_path: Path = resources.SHD_DEFAULT_N
        self._ao_path: Path = resources.SHD_DEFAULT_AO
        self._height_path: Path = resources.SHD_DEFAULT_H
        # math values
        self._index_count: int = 0
        self._vao: int = 0
        self._vertex_buffer: int = 0
        self._index_buffer: int = 0
        self._shader_program: int = 0
        self._albedo_texture: int = 0
        self._metallic_texture: int = 0
        self._roughness_texture: int = 0
        self._normal_texture: int = 0
        self._ao_texture: int = 0
        self._height_texture: int = 0
        self._height_scale: float = 0.05
        self._rotation_x: float = -20.0
        self._rotation_y: float = 30.0
        self._distance: float = 4.0
        self._light_azimuth: float = -120.0
        self._last_mouse_pos: QtCore.QPoint = QtCore.QPoint()

        self.setMinimumSize(400, 400)

    def initializeGL(self) -> None:
        gl.glClearColor(0.05, 0.05, 0.07, 1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_FRAMEBUFFER_SRGB)

        self._shader_program = compile_shader_program(
            SHADER_DIR / "pbr.vert", SHADER_DIR / "pbr.frag"
        )
        self._albedo_texture = load_texture(self._albedo_path, srgb=True)
        self._metallic_texture = load_texture(self._metallic_path, srgb=False)
        self._roughness_texture = load_texture(self._roughness_path, srgb=False)
        self._normal_texture = (
            load_texture(self._normal_path, srgb=False)
            if self._normal_path
            else create_solid_texture((128, 128, 255, 255))
        )
        self._ao_texture = (
            load_texture(self._ao_path, srgb=False)
            if self._ao_path
            else create_solid_texture((255, 255, 255, 255))
        )
        self._height_texture = (
            load_texture(self._height_path, srgb=False)
            if self._height_path
            else create_solid_texture((0, 0, 0, 255))
        )
        self._load_mesh()

    def _load_mesh(self) -> None:
        interleaved, indices = load_obj(self._obj_path)
        self._index_count = len(indices)

        xs = interleaved[0::8]
        ys = interleaved[1::8]
        zs = interleaved[2::8]
        center_x = (min(xs) + max(xs)) / 2.0
        center_y = (min(ys) + max(ys)) / 2.0
        center_z = (min(zs) + max(zs)) / 2.0
        extent = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
        self._distance = extent * 1.5 if extent > 0.0 else 4.0

        for vertex_offset in range(0, len(interleaved), 8):
            interleaved[vertex_offset] -= center_x
            interleaved[vertex_offset + 1] -= center_y
            interleaved[vertex_offset + 2] -= center_z

        interleaved = compute_tangents(interleaved, indices)

        vertex_array = numpy.array(interleaved, dtype=numpy.float32)
        index_array = numpy.array(indices, dtype=numpy.uint32)

        self._vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self._vao)

        self._vertex_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vertex_buffer)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, vertex_array.nbytes, vertex_array, gl.GL_STATIC_DRAW
        )

        self._index_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._index_buffer)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            index_array.nbytes,
            index_array,
            gl.GL_STATIC_DRAW,
        )

        stride = 11 * 4
        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE, stride, ctypes.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(
            1, 3, gl.GL_FLOAT, gl.GL_FALSE, stride, ctypes.c_void_p(3 * 4)
        )
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(
            2, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, ctypes.c_void_p(6 * 4)
        )
        gl.glEnableVertexAttribArray(2)
        gl.glVertexAttribPointer(
            3, 3, gl.GL_FLOAT, gl.GL_FALSE, stride, ctypes.c_void_p(8 * 4)
        )
        gl.glEnableVertexAttribArray(3)

        gl.glBindVertexArray(0)

    def set_albedo_texture(self, image: Optional[numpy.ndarray]) -> None:
        """
        Replace the albedo texture and trigger a repaint.

        Args:
            image (Optional[numpy.ndarray]): New albedo image data as a 2D or
                3D uint8 array.
        """
        self.makeCurrent()
        gl.glDeleteTextures(1, [self._albedo_texture])
        if image is None:
            self._albedo_texture = load_texture(self._albedo_path, srgb=True)
        else:
            self._albedo_texture = create_texture_from_array(image, srgb=True)
        self.doneCurrent()
        self.update()

    def set_metallic_texture(self, image: Optional[numpy.ndarray]) -> None:
        """
        Replace the metallic texture and trigger a repaint.

        Args:
            image (Optional[numpy.ndarray]): New metallic image data as a 2D or
                3D uint8 array.
        """
        self.makeCurrent()
        gl.glDeleteTextures(1, [self._metallic_texture])
        if image is None:
            self._metallic_texture = load_texture(self._metallic_path, srgb=False)
        else:
            self._metallic_texture = create_texture_from_array(image, srgb=False)
        self.doneCurrent()
        self.update()

    def set_roughness_texture(self, image: Optional[numpy.ndarray]) -> None:
        """
        Replace the roughness texture and trigger a repaint.

        Args:
            image (Optional[numpy.ndarray]): New roughness image data as a 2D
                or 3D uint8 array.
        """
        self.makeCurrent()
        gl.glDeleteTextures(1, [self._roughness_texture])
        if image is None:
            self._roughness_texture = load_texture(self._roughness_path, srgb=False)
        else:
            self._roughness_texture = create_texture_from_array(image, srgb=False)
        self.doneCurrent()
        self.update()

    def set_normal_texture(self, image: Optional[numpy.ndarray]) -> None:
        """
        Replace the normal map texture and trigger a repaint.

        Args:
            image (Optional[numpy.ndarray]): New normal map image data as a 2D
                or 3D uint8 array.
        """
        self.makeCurrent()
        gl.glDeleteTextures(1, [self._normal_texture])
        if image is None:
            self._normal_texture = load_texture(self._normal_path, srgb=False)
        else:
            self._normal_texture = create_texture_from_array(image, srgb=False)
        self.doneCurrent()
        self.update()

    def set_ao_texture(self, image: Optional[numpy.ndarray]) -> None:
        """
        Replace the ambient occlusion texture and trigger a repaint.

        Args:
            image (Optional[numpy.ndarray]): New ambient occlusion image data
            as a 2D or 3D uint8 array.
        """
        self.makeCurrent()
        gl.glDeleteTextures(1, [self._ao_texture])
        if image is None:
            self._ao_texture = load_texture(self._ao_path, srgb=False)
        else:
            self._ao_texture = create_texture_from_array(image, srgb=False)
        self.doneCurrent()
        self.update()

    def set_height_texture(self, image: Optional[numpy.ndarray]) -> None:
        """
        Replace the height map texture and trigger a repaint.

        Args:
            image (Optional[numpy.ndarray]): New height map image data as a 2D
                or 3D uint8 array.
        """
        self.makeCurrent()
        gl.glDeleteTextures(1, [self._height_texture])
        if image is None:
            self._height_texture = load_texture(self._height_path, srgb=False)
        else:
            self._height_texture = create_texture_from_array(image, srgb=False)
        self.doneCurrent()
        self.update()

    def resizeGL(self, width: int, height: int) -> None:
        gl.glViewport(0, 0, width, height)

    def paintGL(self) -> None:
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        if self._index_count == 0:
            return

        width = max(self.width(), 1)
        height = max(self.height(), 1)
        aspect_ratio = width / height

        model = matrix.rotation_y(self._rotation_y) @ matrix.rotation_x(
            self._rotation_x
        )
        view = matrix.translation(0.0, 0.0, -self._distance)
        near = max(self._distance * 0.01, 0.01)
        far = self._distance * 10.0
        projection = matrix.perspective(45.0, aspect_ratio, near, far)
        normal_matrix = matrix.normal_matrix(model)

        camera_position = numpy.array([0.0, 0.0, self._distance], dtype=numpy.float32)
        light_yaw = math.radians(self._light_azimuth)
        light_direction = numpy.array(
            [math.sin(light_yaw), -1.0, math.cos(light_yaw)], dtype=numpy.float32
        )
        light_color = numpy.array([3.0, 3.0, 3.0], dtype=numpy.float32)
        ambient_color = numpy.array([0.05, 0.05, 0.06], dtype=numpy.float32)

        gl.glUseProgram(self._shader_program)
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self._shader_program, "u_model"),
            1,
            gl.GL_TRUE,
            model,
        )
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self._shader_program, "u_view"), 1, gl.GL_TRUE, view
        )
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self._shader_program, "u_projection"),
            1,
            gl.GL_TRUE,
            projection,
        )
        gl.glUniformMatrix3fv(
            gl.glGetUniformLocation(self._shader_program, "u_normal_matrix"),
            1,
            gl.GL_TRUE,
            normal_matrix,
        )
        gl.glUniform3fv(
            gl.glGetUniformLocation(self._shader_program, "u_camera_position"),
            1,
            camera_position,
        )
        gl.glUniform3fv(
            gl.glGetUniformLocation(self._shader_program, "u_light_direction"),
            1,
            light_direction,
        )
        gl.glUniform3fv(
            gl.glGetUniformLocation(self._shader_program, "u_light_color"),
            1,
            light_color,
        )
        gl.glUniform3fv(
            gl.glGetUniformLocation(self._shader_program, "u_ambient_color"),
            1,
            ambient_color,
        )
        gl.glUniform1f(
            gl.glGetUniformLocation(self._shader_program, "u_height_scale"),
            self._height_scale,
        )

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._albedo_texture)
        gl.glUniform1i(gl.glGetUniformLocation(self._shader_program, "u_albedo_map"), 0)

        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._metallic_texture)
        gl.glUniform1i(
            gl.glGetUniformLocation(self._shader_program, "u_metallic_map"), 1
        )

        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._roughness_texture)
        gl.glUniform1i(
            gl.glGetUniformLocation(self._shader_program, "u_roughness_map"), 2
        )

        gl.glActiveTexture(gl.GL_TEXTURE3)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._normal_texture)
        gl.glUniform1i(gl.glGetUniformLocation(self._shader_program, "u_normal_map"), 3)

        gl.glActiveTexture(gl.GL_TEXTURE4)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._ao_texture)
        gl.glUniform1i(gl.glGetUniformLocation(self._shader_program, "u_ao_map"), 4)

        gl.glActiveTexture(gl.GL_TEXTURE5)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._height_texture)
        gl.glUniform1i(gl.glGetUniformLocation(self._shader_program, "u_height_map"), 5)

        gl.glBindVertexArray(self._vao)
        gl.glDrawElements(gl.GL_TRIANGLES, self._index_count, gl.GL_UNSIGNED_INT, None)
        gl.glBindVertexArray(0)
        gl.glUseProgram(0)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self._last_mouse_pos = event.position().toPoint()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        current_pos = event.position().toPoint()
        delta = current_pos - self._last_mouse_pos
        shift_held = event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier
        right_button_held = event.buttons() & QtCore.Qt.MouseButton.RightButton
        if shift_held and right_button_held:
            self._light_azimuth += delta.x() * 0.5
        else:
            self._rotation_y += delta.x() * 0.5
            self._rotation_x += delta.y() * 0.5
        self._last_mouse_pos = current_pos
        self.update()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        zoom_factor = 0.9 if event.angleDelta().y() > 0 else 1.1
        self._distance *= zoom_factor
        self._distance = max(0.01, min(self._distance, 1000.0))
        self.update()
