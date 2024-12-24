import pytest
import os
import base64
import requests
from PIL import Image
from dotenv import load_dotenv
from swarmauri.utils.base64_to_img_url import base64_to_img_url

# Load environment variables
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("IMGBB_API_KEY")

# Path to the test image
TEST_IMAGE_PATH = "pkgs/swarmauri/tests/static/cityscape.png"


@pytest.mark.skipif(
    not API_KEY, reason="IMGBB_API_KEY is not set in the environment variables"
)
@pytest.mark.unit
def test_base64_to_img_url():
    # Ensure the test image file exists
    assert os.path.exists(TEST_IMAGE_PATH), f"Test image not found at {TEST_IMAGE_PATH}"

    # Read the image file and encode it to base64
    with open(TEST_IMAGE_PATH, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode()

    # Call the function with the base64 string and API key
    image_url = base64_to_img_url(
        base64_str=base64_string,
        api_key=API_KEY,
    )

    # Assert that we got a URL back
    assert isinstance(image_url, str), "Expected a string URL, but got a different type"
    assert image_url.startswith("http"), "Expected URL to start with 'http'"

    # Optionally, check if the URL is accessible
    response = requests.get(image_url)
    assert (
        response.status_code == 200
    ), f"Failed to access the uploaded image at {image_url}"
