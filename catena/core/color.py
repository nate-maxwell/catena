"""
Various helpers for converting between normal file RGB channel layout to OpenCV
BGR channel layout.
"""

import cv2
import numpy as np
from PySide6TK import QtGui


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """
    Convert a BGR image array to RGB.

    Args:
        image (np.ndarray): Image in BGR order, as returned by cv2.imread.
    Returns:
        np.ndarray: Image in RGB order.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def rgb_to_bgr(image: np.ndarray) -> np.ndarray:
    """
    Convert an RGB image array to BGR.

    Args:
        image (np.ndarray): Image in RGB order.
    Returns:
        np.ndarray: Image in BGR order, suitable for cv2 functions.
    """
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def ndarray_to_qimage(image: np.ndarray) -> QtGui.QImage:
    """
    Convert an RGB numpy array to a QImage.

    Args:
        image (np.ndarray): Image in RGB order, contiguous, dtype uint8.
    Returns:
        QtGui.QImage: The resulting QImage. Note the underlying buffer is
            shared with `image`; copy the QImage if the array may be
            mutated or garbage collected afterward.
    """
    image = np.ascontiguousarray(image)
    height, width, channels = image.shape
    bytes_per_line = width * channels
    qimage = QtGui.QImage(
        image.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_RGB888
    )
    return qimage.copy()
