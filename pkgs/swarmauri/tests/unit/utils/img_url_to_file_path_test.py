import pytest
import os
import requests
from PIL import Image
from io import BytesIO
from unittest.mock import patch
from swarmauri.utils.img_url_to_file_path import img_url_to_file_path


def test_img_url_to_file_path(tmp_path):
    # Create a sample image in memory
    img = Image.new("RGB", (10, 10), color="blue")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_data = buffered.getvalue()

    # Mock the response from requests.get to return our image data
    mock_response = requests.models.Response()
    mock_response.status_code = 200
    mock_response._content = img_data

    with patch("swarmauri.utils.img_url_to_file_path.requests.get") as mock_get:
        mock_get.return_value = mock_response

        # Define the file path where the image will be saved
        output_image_path = os.path.join(tmp_path, "output_image.png")

        # Call the function with a dummy URL and file path
        img_url_to_file_path("http://example.com/fake-image-url", output_image_path)

        # Assert that the file was created
        assert os.path.exists(output_image_path), "The image file was not created."

        # Optionally, open the saved image and verify its content
        saved_image = Image.open(output_image_path)
        assert saved_image.size == (10, 10), "The saved image has incorrect dimensions."
        assert saved_image.format == "PNG", "The saved image is not in PNG format."

        # Cleanup (handled automatically by tmp_path)
