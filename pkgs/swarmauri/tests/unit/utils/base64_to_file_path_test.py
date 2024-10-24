import pytest
import base64
from PIL import Image
from io import BytesIO
import os

# Import the function to be tested
from swarmauri.utils.base64_to_file_path import base64_to_file_path


@pytest.fixture
def sample_image():
    # Create a simple 10x10 red image
    image = Image.new("RGB", (10, 10), color="red")
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def test_base64_to_file_path(sample_image, tmp_path):
    # Create a temporary file path
    file_path = tmp_path / "test_image.png"

    # Call the function
    base64_to_file_path(sample_image, str(file_path))

    # Check if the file exists
    assert file_path.exists()

    # Open the saved image
    saved_image = Image.open(file_path)

    # Check if the image has the correct size and color
    assert saved_image.size == (10, 10)
    assert saved_image.getpixel((5, 5)) == (255, 0, 0)  # Red color

    # Clean up
    saved_image.close()
