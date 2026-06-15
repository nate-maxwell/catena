import ctypes
import math
from pathlib import Path
from typing import Optional

import OpenGL.GL as gl
import numpy
from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtOpenGLWidgets
from PySide6TK import QtWidgets

from catena.core import resources
from catena.core import texture
from catena.core.panes.obj_viewer import matrix
from catena.core.panes.obj_viewer import shader

SHADER_DIR = Path(__file__).parent


class ObjViewer(QtOpenGLWidgets.QOpenGLWidget):
    """An OpenGL widget that displays a PBR-shaded OBJ mesh with mouse-based orbit controls."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        # object
        self._obj_path: Path = resources.GEO_CUBE

        # textures
        self._albedo_path: Path = resources.SHD_DEFAULT_BC
        self._metallic_path: Path = resources.SHD_DEFAULT_M
        self._roughness_path: Path = resources.SHD_DEFAULT_R
        self._normal_path: Path = resources.SHD_DEFAULT_N
        self._ao_path: Path = resources.SHD_DEFAULT_AO
        self._height_path: Path = resources.SHD_DEFAULT_H
        self._environment_path: Path = resources.HDR_DEFAULT

        # texture math values
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
        self._environment_blur_texture = texture.load_hdr_texture_blurred(
            self._environment_path
        )
        self._environment_strength: float = 1.0

        # viewport math values
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
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_FRAMEBUFFER_SRGB)

        self._shader_program = shader.compile_shader_program(
            SHADER_DIR / "pbr.vert", SHADER_DIR / "pbr.frag"
        )
        self._albedo_texture = texture.load_texture(self._albedo_path, srgb=True)
        self._metallic_texture = texture.load_texture(self._metallic_path, srgb=False)
        self._roughness_texture = texture.load_texture(self._roughness_path, srgb=False)
        self._normal_texture = (
            texture.load_normal_texture(self._normal_path)
            if self._normal_path
            else texture.create_solid_texture((128, 128, 255, 255))
        )
        self._ao_texture = (
            texture.load_texture(self._ao_path, srgb=False)
            if self._ao_path
            else texture.create_solid_texture((255, 255, 255, 255))
        )
        self._height_texture = (
            texture.load_texture(self._height_path, srgb=False)
            if self._height_path
            else texture.create_solid_texture((0, 0, 0, 255))
        )

        try:
            self._environment_texture = (
                texture.load_hdr_texture(self._environment_path)
                if self._environment_path
                else texture.create_solid_texture((64, 64, 64, 255))
            )
            self._environment_blur_texture = (
                texture.load_hdr_texture_blurred(self._environment_path)
                if self._environment_path
                else texture.create_solid_texture((64, 64, 64, 255))
            )
        except Exception as error:
            print(
                f"Failed to load HDRI environment: {self._environment_path} ({error})"
            )
            self._environment_texture = texture.create_solid_texture((64, 64, 64, 255))
            self._environment_blur_texture = texture.create_solid_texture(
                (64, 64, 64, 255)
            )

        self._load_mesh()

    def _load_mesh(self) -> None:
        interleaved, indices = shader.load_obj(self._obj_path)
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

        interleaved = shader.compute_tangents(interleaved, indices)

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
            self._albedo_texture = texture.load_texture(self._albedo_path, srgb=True)
        else:
            self._albedo_texture = texture.create_texture_from_array(image, srgb=True)
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
            self._metallic_texture = texture.load_texture(
                self._metallic_path, srgb=False
            )
        else:
            self._metallic_texture = texture.create_texture_from_array(
                image, srgb=False
            )
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
            self._roughness_texture = texture.load_texture(
                self._roughness_path, srgb=False
            )
        else:
            self._roughness_texture = texture.create_texture_from_array(
                image, srgb=False
            )
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
            self._normal_texture = texture.load_normal_texture(self._normal_path)
        else:
            self._normal_texture = texture.create_texture_from_array(
                image,
                srgb=False,
                invert_green_after_flip=True,
            )
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
            self._ao_texture = texture.load_texture(self._ao_path, srgb=False)
        else:
            self._ao_texture = texture.create_texture_from_array(image, srgb=False)
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
            self._height_texture = texture.load_texture(self._height_path, srgb=False)
        else:
            self._height_texture = texture.create_texture_from_array(image, srgb=False)
        self.doneCurrent()
        self.update()

    def set_model(self, obj_path: Path) -> None:
        """
        Replace the displayed mesh and trigger a repaint.

        Args:
            obj_path (Path): Path to the new .obj file.
        """
        self.makeCurrent()
        gl.glDeleteVertexArrays(1, [self._vao])
        gl.glDeleteBuffers(1, [self._vertex_buffer])
        gl.glDeleteBuffers(1, [self._index_buffer])
        self._obj_path = obj_path
        self._load_mesh()
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

        gl.glActiveTexture(gl.GL_TEXTURE6)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._environment_texture)
        gl.glUniform1i(
            gl.glGetUniformLocation(self._shader_program, "u_environment_map"),
            6,
        )
        gl.glUniform1f(
            gl.glGetUniformLocation(self._shader_program, "u_environment_strength"),
            self._environment_strength,
        )

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
