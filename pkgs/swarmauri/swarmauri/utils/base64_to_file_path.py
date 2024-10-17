import base64
from PIL import Image
from io import BytesIO
from typing import Union

def base64_to_file_path(base64_str: str, file_path: str) -> None:
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))
    image.save(file_path)
