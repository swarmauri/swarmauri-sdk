import io
import base64
import requests
from PIL import Image
from typing import Union


def in_memory_img_to_img_url(image: Image.Image, api_key: str) -> str:
    """
    Convert an in-memory PIL Image to a URL by uploading to ImgBB.
    Get your IMGBB API key from: https://api.imgbb.com/
    Args:
    image (Image.Image): The in-memory PIL Image.
    api_key (str): The ImgBB API key.

    Returns:
    str: The URL of the uploaded image.

    Raises:
    Exception: If the upload fails.
    """
    # ImgBB API endpoint
    url = "https://api.imgbb.com/1/upload"

    # Convert PIL Image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Prepare the payload
    payload = {
        "key": api_key,
        "image": img_str,
    }

    # Send POST request to ImgBB API
    response = requests.post(url, payload)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            return data["data"]["url"]
        else:
            raise Exception(
                "Failed to upload image: "
                + data.get("error", {}).get("message", "Unknown error")
            )
    else:
        raise Exception(f"Failed to upload image. Status code: {response.status_code}")
