"""Validation utilities for files and form inputs."""

import io
import re
from pathlib import Path
from PIL import Image
from config import settings
from core.exceptions import ValidationError


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal or unsafe characters."""
    base = Path(filename).name
    # Keep alphanumeric, dot, dash, underscore
    cleaned = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", base)
    return cleaned[:100]


def validate_image_file(file_bytes: bytes, original_name: str, raise_exception: bool = True):
    """Validate uploaded image format, size, and integrity.

    Raises ValidationError if invalid and raise_exception is True.
    """
    if not file_bytes:
        if raise_exception:
            raise ValidationError("File is empty.")
        return False, "File is empty."

    if len(file_bytes) > settings.max_upload_size_bytes:
        msg = f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB} MB."
        if raise_exception:
            raise ValidationError(msg)
        return False, msg

    ext = Path(original_name).suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        msg = f"Unsupported file extension '{ext}'. Only JPG, JPEG, and PNG are supported."
        if raise_exception:
            raise ValidationError(msg)
        return False, msg

    # Validate image header and structure with PIL
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()  # Verifies file integrity
        format_name = (image.format or "").upper()
        if format_name not in ["JPEG", "PNG"]:
            msg = f"Unsupported image format: {format_name}."
            if raise_exception:
                raise ValidationError(msg)
            return False, msg
    except Exception:
        msg = "Invalid image file: File is not a valid readable image."
        if raise_exception:
            raise ValidationError(msg)
        return False, msg

    if raise_exception:
        return True
    return True, ext
