from typing import Union
from PIL import Image
import requests
from io import BytesIO

def img_url_to_in_memory_img(img_url: str) -> Image.Image:
    response = requests.get(img_url)
    image = Image.open(BytesIO(response.content))
    return image
