"""Tests for Image Upload Validation and Filename Sanitization."""

import pytest
import io
from PIL import Image
from utils.validation import validate_image_file, sanitize_filename
from core.exceptions import ValidationError


def create_test_image_bytes(format="JPEG", size=(100, 100), color=(0, 128, 0)):
    """Helper to generate valid image bytes in memory."""
    buf = io.BytesIO()
    img = Image.new("RGB", size, color)
    img.save(buf, format=format)
    return buf.getvalue()


def test_valid_jpeg_and_png_accepted():
    jpeg_bytes = create_test_image_bytes(format="JPEG")
    assert validate_image_file(jpeg_bytes, "healthy_leaf.jpg") is True

    png_bytes = create_test_image_bytes(format="PNG")
    assert validate_image_file(png_bytes, "healthy_leaf.png") is True


def test_invalid_extension_rejected():
    jpeg_bytes = create_test_image_bytes(format="JPEG")
    with pytest.raises(ValidationError, match="Unsupported file extension"):
        validate_image_file(jpeg_bytes, "script.exe")


def test_fake_image_file_rejected():
    fake_bytes = b"This is a plaintext file renamed to photo.jpg"
    with pytest.raises(ValidationError, match="Invalid image file"):
        validate_image_file(fake_bytes, "photo.jpg")


def test_oversized_file_rejected():
    # 6 MB of dummy data
    large_bytes = b"\xFF\xD8\xFF" + b"0" * (6 * 1024 * 1024)
    with pytest.raises(ValidationError, match="File size exceeds maximum limit"):
        validate_image_file(large_bytes, "huge_photo.jpg")


def test_sanitize_filename():
    assert sanitize_filename("../../etc/passwd.jpg") == "passwd.jpg"
    assert sanitize_filename("my leaf photo (1)!.jpeg") == "my_leaf_photo__1__.jpeg"
