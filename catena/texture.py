"""
Various helpers for converting between normal file RGB channel layout to OpenCV
BGR channel layout.
"""

from enum import Enum
from enum import auto
from pathlib import Path
from typing import Optional

import OpenGL.GL as gl
import imageio.v3 as imageio
import cv2
import numpy
from PySide6TK import QtGui


class TextureType(Enum):
    ALBEDO = auto()
    ROUGHNESS = auto()
    METALLIC = auto()
    AO = auto()
    HEIGHT = auto()
    NORMAL = auto()


def rgb_to_bgr(image: numpy.ndarray) -> numpy.ndarray:
    """
    Convert an RGB image array to BGR.

    Args:
        image (numpy.ndarray): Image in RGB order.
    Returns:
        numpy.ndarray: Image in BGR order, suitable for cv2 functions.
    """
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def rgba_to_bgra(image: numpy.ndarray) -> numpy.ndarray:
    """
    Convert an RGBA image array to BGRA.

    Args:
        image (numpy.ndarray): Image in RGBA order.
    Returns:
        numpy.ndarray: Image in BGRA order, suitable for cv2 functions.
    """
    return cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)


def bgr_to_rgb(image: numpy.ndarray) -> numpy.ndarray:
    """
    Convert a BGR image array to RGB.

    Args:
        image (numpy.ndarray): Image in BGR order, as returned by cv2.imread.
    Returns:
        numpy.ndarray: Image in RGB order.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def bgra_to_rgba(image: numpy.ndarray) -> numpy.ndarray:
    """
    Convert a BGRA image array to RGBA.

    Args:
        image (numpy.ndarray): Image in BGRA order, as returned by cv2.imread.
    Returns:
        numpy.ndarray: Image in RGBA order.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)


def ndarray_to_qimage(image: numpy.ndarray) -> QtGui.QImage:
    """
    Convert an RGB numpy array to a QImage.

    Args:
        image (numpy.ndarray): Image in RGB order, contiguous, dtype uint8.
    Returns:
        QtGui.QImage: The resulting QImage. Note the underlying buffer is
            shared with `image`; copy the QImage if the array may be
            mutated or garbage collected afterward.
    """
    image = numpy.ascontiguousarray(image)
    height, width, channels = image.shape
    bytes_per_line = width * channels
    qimage = QtGui.QImage(
        image.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_RGB888
    )
    return qimage.copy()


def to_uint8(image: numpy.ndarray) -> numpy.ndarray:
    """
    Convert an image array to uint8, scaling floating-point data from 0.0-1.0
    to 0-255.

    Args:
        image (numpy.ndarray): Image data, either uint8 or floating-point in
            range 0.0-1.0.
    Returns:
        numpy.ndarray: Image data as uint8.
    """
    if numpy.issubdtype(image.dtype, numpy.floating):
        image = numpy.clip(image, 0.0, 1.0) * 255.0
        return image.astype(numpy.uint8)
    return image.astype(numpy.uint8)


def create_texture_from_array(
    image: numpy.ndarray,
    srgb: bool,
    invert_green_after_flip: bool = False,
) -> int:
    """
    Upload an image array into an OpenGL 2D texture.

    Args:
        image (numpy.ndarray): Image data as a 2D (grayscale) or 3D (RGB/RGBA)
            array, either uint8 in range 0-255 or floating-point in range 0.0-1.0.
        srgb (bool): If True, the texture is stored in an sRGB internal format
            (for albedo/color data). If False, a linear format is used.
        invert_green_after_flip (bool): If True, invert the green channel after
            vertical flipping. Use this for tangent-space normal maps.
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

    if invert_green_after_flip:
        image[..., 1] = 255 - image[..., 1]

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


def load_normal_texture(path: Path) -> int:
    """Load a tangent-space normal map into an OpenGL 2D texture."""
    image = imageio.imread(path)
    return create_texture_from_array(
        image,
        srgb=False,
        invert_green_after_flip=True,
    )


def _load_hdr_image(path: Path) -> Optional[numpy.ndarray]:
    """
    Load an HDR image from disk as RGB float32.

    Args:
        path (Path): Path to an HDR/EXR image.
    Returns:
        numpy.ndarray | None: RGB float32 image, or None if loading failed.
    """
    if path is None or not path.exists():
        return None

    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None:
        return None

    original_dtype = image.dtype

    if image.ndim == 2:
        image = numpy.stack([image, image, image], axis=-1)
    elif image.ndim == 3 and image.shape[2] == 3:
        image = bgr_to_rgb(image)
    elif image.ndim == 3 and image.shape[2] == 4:
        image = bgra_to_rgba(image)
        image = image[..., :3]
    else:
        return None

    image = image.astype(numpy.float32)

    if not numpy.isfinite(image).all():
        image = numpy.nan_to_num(image, nan=0.0, posinf=1.0, neginf=0.0)

    if original_dtype == numpy.uint8:
        image = image / 255.0
    elif original_dtype == numpy.uint16:
        image = image / 65535.0

    image = numpy.clip(image, 0.0, None)
    return image


def _upload_hdr_texture(image: numpy.ndarray) -> int:
    """
    Upload an RGB float32 image as an OpenGL HDR texture.

    Args:
        image (numpy.ndarray): RGB float32 image.
    Returns:
        int: OpenGL texture handle.
    """
    image = numpy.flipud(image)
    image = numpy.ascontiguousarray(image.astype(numpy.float32))

    texture_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGB16F,
        image.shape[1],
        image.shape[0],
        0,
        gl.GL_RGB,
        gl.GL_FLOAT,
        image,
    )

    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
    gl.glTexParameteri(
        gl.GL_TEXTURE_2D,
        gl.GL_TEXTURE_MIN_FILTER,
        gl.GL_LINEAR_MIPMAP_LINEAR,
    )
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

    return texture_id


def load_hdr_texture(path: Path) -> int:
    """
    Load an HDR/equirectangular environment texture.

    Args:
        path (Path): Path to an HDR or EXR image.
    Returns:
        int: OpenGL texture handle.
    """
    image = _load_hdr_image(path)
    if image is None:
        return create_solid_texture((64, 64, 64, 255))

    return _upload_hdr_texture(image)


def load_hdr_texture_blurred(path: Path) -> int:
    """
    Load a blurred HDR/equirectangular environment texture.

    This is a practical anti-firefly approximation for viewport environment
    lighting. It is not physically correct prefiltered IBL, but it avoids direct
    sampling of tiny, extremely bright HDR pixels.

    Args:
        path (Path): Path to an HDR or EXR image.
    Returns:
        int: OpenGL texture handle.
    """
    image = _load_hdr_image(path)
    if image is None:
        return create_solid_texture((64, 64, 64, 255))

    target_width = 128
    target_height = max(1, target_width * image.shape[0] // image.shape[1])

    image = cv2.resize(
        image,
        (target_width, target_height),
        interpolation=cv2.INTER_AREA,
    )

    image = cv2.GaussianBlur(
        image,
        ksize=(0, 0),
        sigmaX=8.0,
        sigmaY=8.0,
    )

    image = numpy.clip(image, 0.0, None)

    return _upload_hdr_texture(image)


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
