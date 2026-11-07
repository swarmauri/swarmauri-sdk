from io import BytesIO

import httpx
from PIL import Image


def img_url_to_in_memory_img(img_url: str) -> Image.Image:
    """Fetch an image with an explicit five-second inactivity timeout."""
    response = httpx.get(img_url, timeout=5.0)
    image = Image.open(BytesIO(response.content))
    return image
