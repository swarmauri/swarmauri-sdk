from PIL import Image
import httpx
from io import BytesIO


def img_url_to_in_memory_img(img_url: str) -> Image.Image:
    response = httpx.get(img_url, timeout=10.0)
    image = Image.open(BytesIO(response.content))
    return image
