import base64
from io import BytesIO
import httpx
from PIL import Image


def img_url_to_base64(img_url: str) -> str:
    response = httpx.get(img_url)
    image = Image.open(BytesIO(response.content))
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
