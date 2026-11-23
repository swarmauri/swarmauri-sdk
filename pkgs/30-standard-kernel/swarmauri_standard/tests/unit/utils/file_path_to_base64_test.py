import base64
import os
from io import BytesIO
from pathlib import Path

from PIL import Image
from swarmauri_standard.utils.file_path_to_base64 import file_path_to_base64

# Get the current working directory
root_dir = Path(__file__).resolve().parents[2]

test_image_path = os.path.join(root_dir, "static", "cityscape.png")


def test_file_path_to_base64():
    # Call the function to get the base64 result
    result = file_path_to_base64(test_image_path)

    # PNG re-encoding can change compression without changing image pixels.
    with Image.open(test_image_path) as expected:
        with Image.open(BytesIO(base64.b64decode(result))) as actual:
            assert actual.format == "PNG"
            assert actual.mode == expected.mode
            assert actual.size == expected.size
            assert actual.tobytes() == expected.tobytes()
