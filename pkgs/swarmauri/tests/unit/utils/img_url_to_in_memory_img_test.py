import pytest
import requests
from PIL import Image
from io import BytesIO
from unittest.mock import patch
from swarmauri.utils.img_url_to_in_memory_img import img_url_to_in_memory_img


def test_img_url_to_in_memory_img():
    # Create a sample image in memory (RGB, 10x10, red)
    img = Image.new("RGB", (10, 10), color="red")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_data = buffered.getvalue()

    # Mock the response from requests.get to return our image data
    mock_response = requests.models.Response()
    mock_response.status_code = 200
    mock_response._content = img_data

    with patch("swarmauri.utils.img_url_to_in_memory_img.requests.get") as mock_get:
        mock_get.return_value = mock_response

        # Call the function with a dummy URL
        result_image = img_url_to_in_memory_img("http://example.com/fake-image-url")

        # Assert the result is a valid PIL Image object
        assert isinstance(
            result_image, Image.Image
        ), "The result is not a PIL Image object."

        # Assert the dimensions of the image are correct
        assert result_image.size == (10, 10), "The image has incorrect dimensions."

        # Assert the image mode is correct (RGB)
        assert result_image.mode == "RGB", "The image mode is not RGB."
