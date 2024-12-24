import requests
import base64
from typing import Union
from PIL import Image


def file_path_to_img_url(file_path: str, api_key: str) -> str:
    """
    Convert an image in a specified path to a URL by uploading to ImgBB.
    Get your IMGBB API key from: https://api.imgbb.com/

    Args:
    file_path (str): The path of the image.
    api_key (str): The ImgBB API key.

    Returns:
    str: The URL of the uploaded image.

    Raises:
    Exception: If the upload fails.
    """
    url = "https://api.imgbb.com/1/upload"

    # Open and encode the image file
    with open(file_path, "rb") as file:
        payload = {
            "key": api_key,
            "image": base64.b64encode(file.read()),
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
