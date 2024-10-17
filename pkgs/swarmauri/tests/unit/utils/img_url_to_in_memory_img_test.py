import pytest
from PIL import Image
from swarmauri.utils.img_url_to_in_memory_img import img_url_to_in_memory_img  # Adjust the path

@pytest.fixture
def mock_img_url():
    return 'https://via.placeholder.com/150'  # Use a placeholder image

@pytest.mark.unit
def test_img_url_to_in_memory_img(mock_img_url):
    img = img_url_to_in_memory_img(mock_img_url)
    assert isinstance(img, Image.Image)
