"""Protect the explicit HTTPX inactivity timeout for image loading."""

from io import BytesIO
from unittest.mock import Mock

import httpx
import pytest
from PIL import Image
from swarmauri_standard.utils.img_url_to_in_memory_img import (
    img_url_to_in_memory_img,
)


@pytest.mark.unit
def test_image_fetch_uses_five_second_inactivity_timeout(monkeypatch):
    payload = BytesIO()
    with Image.new("RGB", (2, 1), "red") as image:
        image.save(payload, format="PNG")
    get = Mock(return_value=httpx.Response(200, content=payload.getvalue()))
    monkeypatch.setattr(httpx, "get", get)

    url = "https://example.invalid/example.png"
    with img_url_to_in_memory_img(url) as image:
        assert image.size == (2, 1)
        assert image.getpixel((0, 0)) == (255, 0, 0)

    get.assert_called_once_with(url, timeout=5.0)
