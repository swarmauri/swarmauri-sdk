import pytest
import os
import requests
from swarmauri.utils.file_path_to_img_url import file_path_to_img_url
from dotenv import load_dotenv

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
def test_file_path_to_img_url():
    # Ensure the test image file exists
    assert os.path.exists(TEST_IMAGE_PATH), f"Test image not found at {TEST_IMAGE_PATH}"

    # Call the function with the real API key and image file
    image_url = file_path_to_img_url(
        file_path=TEST_IMAGE_PATH,
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
