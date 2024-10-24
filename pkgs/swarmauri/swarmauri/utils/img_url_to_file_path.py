import requests
from PIL import Image
from io import BytesIO

def img_url_to_file_path(img_url: str, file_path: str) -> None:
    response = requests.get(img_url)
    image = Image.open(BytesIO(response.content))
    image.save(file_path)