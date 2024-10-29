import pytest
import base64
from swarmauri.utils.file_path_to_base64 import file_path_to_base64
import os
from pathlib import Path

# Get the current working directory
root_dir = Path(__file__).resolve().parents[2]

test_image_path = os.path.join(root_dir, "static", "cityscape.png")


def test_file_path_to_base64():
    # Call the function to get the base64 result
    result = file_path_to_base64(test_image_path)

    # Manually load the image and convert it to base64 to compare
    with open(test_image_path, "rb") as img_file:
        expected = base64.b64encode(img_file.read()).decode("utf-8")

    # Assert the result is the expected base64 string
    assert (
        result == expected
    ), "Base64 conversion of the image does not match the expected output."
