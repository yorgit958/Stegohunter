"""
Image loader utility.
Handles loading images from file bytes, file paths, or URLs into NumPy arrays.
"""

import io
import numpy as np
import cv2
from typing import Optional


def load_image_from_bytes(file_bytes: bytes) -> Optional[np.ndarray]:
    """
    Load an image from raw bytes into a NumPy array.

    Args:
        file_bytes: Raw image file bytes (PNG, JPEG, BMP, etc.)

    Returns:
        NumPy array of shape (H, W, C) in BGR format, or None if loading fails.
    """
    try:
        nparr = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception:
        return None


def load_image_from_path(file_path: str) -> Optional[np.ndarray]:
    """
    Load an image from a file path.

    Args:
        file_path: Path to the image file.

    Returns:
        NumPy array of shape (H, W, C) in BGR format, or None if loading fails.
    """
    try:
        image = cv2.imread(file_path, cv2.IMREAD_COLOR)
        return image
    except Exception:
        return None


def get_image_info(image: np.ndarray) -> dict:
    """Extract basic image metadata."""
    if image is None:
        return {}

    height, width = image.shape[:2]
    channels = image.shape[2] if len(image.shape) == 3 else 1

    return {
        "width": width,
        "height": height,
        "channels": channels,
        "total_pixels": width * height,
        "dtype": str(image.dtype),
    }
