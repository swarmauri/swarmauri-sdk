from io import BytesIO

import httpx
from PIL import Image


def img_url_to_in_memory_img(img_url: str) -> Image.Image:
    response = httpx.get(img_url, timeout=10.0)
    image = Image.open(BytesIO(response.content))
    return image
