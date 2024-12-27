import base64
from PIL import Image
from io import BytesIO
from typing import Union

def base64_to_in_memory_img(base64_str: str) -> Image.Image:
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))
    return image
