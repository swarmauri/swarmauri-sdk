import base64
from PIL import Image
from io import BytesIO


def file_path_to_base64(file_path: str) -> str:
    image = Image.open(file_path)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
