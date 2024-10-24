import base64
from PIL import Image
from typing import Union
from io import BytesIO

def in_memory_img_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
