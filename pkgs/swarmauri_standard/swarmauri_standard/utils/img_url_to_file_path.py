from io import BytesIO

import httpx
from PIL import Image


def img_url_to_file_path(img_url: str, file_path: str) -> None:
    response = httpx.get(img_url)
    image = Image.open(BytesIO(response.content))
    image.save(file_path)
