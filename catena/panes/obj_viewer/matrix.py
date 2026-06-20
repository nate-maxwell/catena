import math

import numpy


def perspective(
    fov_y_degrees: float, aspect_ratio: float, near: float, far: float
) -> numpy.ndarray:
    """
    Build a perspective projection matrix.

    Args:
        fov_y_degrees (float): Vertical field of view in degrees.
        aspect_ratio (float): Viewport width divided by height.
        near (float): Near clipping plane distance.
        far (float): Far clipping plane distance.
    Returns:
        numpy.ndarray: Column-major 4x4 projection matrix (float32).
    """
    f = 1.0 / math.tan(math.radians(fov_y_degrees) / 2.0)
    matrix = numpy.zeros((4, 4), dtype=numpy.float32)
    matrix[0, 0] = f / aspect_ratio
    matrix[1, 1] = f
    matrix[2, 2] = (far + near) / (near - far)
    matrix[2, 3] = (2.0 * far * near) / (near - far)
    matrix[3, 2] = -1.0
    return matrix


def translation(x: float, y: float, z: float) -> numpy.ndarray:
    """
    Build a translation matrix.

    Args:
        x (float): Translation along the x axis.
        y (float): Translation along the y axis.
        z (float): Translation along the z axis.
    Returns:
        numpy.ndarray: Column-major 4x4 translation matrix (float32).
    """
    matrix = numpy.identity(4, dtype=numpy.float32)
    matrix[0, 3] = x
    matrix[1, 3] = y
    matrix[2, 3] = z
    return matrix


def rotation_x(angle_degrees: float) -> numpy.ndarray:
    """
    Build a rotation matrix around the x axis.

    Args:
        angle_degrees (float): Rotation angle in degrees.
    Returns:
        numpy.ndarray: Column-major 4x4 rotation matrix (float32).
    """
    angle = math.radians(angle_degrees)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    matrix = numpy.identity(4, dtype=numpy.float32)
    matrix[1, 1] = cos_a
    matrix[1, 2] = -sin_a
    matrix[2, 1] = sin_a
    matrix[2, 2] = cos_a
    return matrix


def rotation_y(angle_degrees: float) -> numpy.ndarray:
    """
    Build a rotation matrix around the y-axis.

    Args:
        angle_degrees (float): Rotation angle in degrees.
    Returns:
        numpy.ndarray: Column-major 4x4 rotation matrix (float32).
    """
    angle = math.radians(angle_degrees)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    matrix = numpy.identity(4, dtype=numpy.float32)
    matrix[0, 0] = cos_a
    matrix[0, 2] = sin_a
    matrix[2, 0] = -sin_a
    matrix[2, 2] = cos_a
    return matrix


def normal_matrix(model_matrix: numpy.ndarray) -> numpy.ndarray:
    """
    Compute the inverse-transpose of the upper-left 3x3 of a model matrix,
    for transforming normals.

    Args:
        model_matrix (numpy.ndarray): 4x4 model matrix (float32).
    Returns:
        numpy.ndarray: 3x3 normal matrix (float32).
    """
    upper_left = model_matrix[:3, :3].astype(numpy.float64)
    inverse = numpy.linalg.inv(upper_left)
    return inverse.T.astype(numpy.float32)
