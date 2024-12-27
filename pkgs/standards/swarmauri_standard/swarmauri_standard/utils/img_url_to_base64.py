import base64
from typing import Union
from io import BytesIO
import requests
from PIL import Image

def img_url_to_base64(img_url: str) -> str:
    response = requests.get(img_url)
    image = Image.open(BytesIO(response.content))
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
