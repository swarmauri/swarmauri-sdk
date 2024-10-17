import base64
import requests
from typing import Union


def base64_to_img_url(base64_str: str, api_key: str) -> str:
    """
    Convert a base64 encoded image string to a URL by uploading to ImgBB.
    Get your IMGBB API key from: https://api.imgbb.com/

    Args:
    base64_str (str): The base64 encoded image string.
    api_key (str): The ImgBB API key.

    Returns:
    str: The URL of the uploaded image.

    Raises:
    Exception: If the upload fails.
    """
    # ImgBB API endpoint
    url = "https://api.imgbb.com/1/upload"

    # Prepare the payload
    payload = {
        "key": api_key,
        "image": base64_str,
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
