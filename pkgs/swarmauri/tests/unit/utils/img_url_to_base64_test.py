import pytest
import base64
from swarmauri.utils.img_url_to_base64 import img_url_to_base64  # Adjust the path

@pytest.fixture
def mock_img_url():
    return 'https://via.placeholder.com/150'

@pytest.mark.unit
def test_img_url_to_base64(mock_img_url):
    img_base64 = img_url_to_base64(mock_img_url)
    assert isinstance(img_base64, str)
    assert img_base64.startswith('iVBOR')  # Checking for common base64 header
