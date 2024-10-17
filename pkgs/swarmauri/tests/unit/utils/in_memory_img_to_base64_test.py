import pytest
from PIL import Image
from swarmauri.utils.in_memory_img_to_base64 import in_memory_img_to_base64  # Adjust the path

@pytest.fixture
def mock_image():
    img = Image.new('RGB', (150, 150), color='blue')
    return img

@pytest.mark.unit
def test_in_memory_img_to_base64(mock_image):
    img_base64 = in_memory_img_to_base64(mock_image)
    assert isinstance(img_base64, str)
    assert img_base64.startswith('iVBOR')  # Checking for common base64 header
