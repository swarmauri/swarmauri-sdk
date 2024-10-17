import pytest
import base64
import requests
from io import BytesIO
from PIL import Image
from unittest.mock import patch
from swarmauri.utils.img_url_to_base64 import img_url_to_base64


def test_img_url_to_base64():
    # Sample image data (we'll use a simple small image for the test)
    img = Image.new("RGB", (10, 10), color="red")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_data = buffered.getvalue()

    # Convert the image to base64 manually for comparison
    expected_base64 = base64.b64encode(img_data).decode("utf-8")

    # Mock the response from requests.get to return our image data
    mock_response = requests.models.Response()
    mock_response.status_code = 200
    mock_response._content = img_data

    with patch("swarmauri.utils.img_url_to_base64.requests.get") as mock_get:
        mock_get.return_value = mock_response

        # Call the function with a dummy URL
        result = img_url_to_base64("http://example.com/fake-image-url")

        # Assert that the base64 result matches the manually encoded base64
        assert (
            result == expected_base64
        ), "The base64 conversion did not match the expected result."
