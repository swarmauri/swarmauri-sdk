from PIL import Image
from typing import Union

def file_path_to_in_memory_img(file_path: str) -> Image.Image:
    image = Image.open(file_path)
    return image
