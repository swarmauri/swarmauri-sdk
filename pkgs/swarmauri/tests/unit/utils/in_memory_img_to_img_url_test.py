import pytest
from PIL import Image
from io import BytesIO
from swarmauri.utils.in_memory_img_to_img_url import in_memory_img_to_img_url  # Adjust the path

@pytest.fixture
def mock_image():
    img = Image.new('RGB', (150, 150), color='red')
    return img

@pytest.fixture
def mock_upload_url():
    return 'https://mockserver.com/upload'

@pytest.mark.unit
def test_in_memory_img_to_img_url(mock_image, mock_upload_url, requests_mock):
    requests_mock.post(mock_upload_url, json={'url': 'https://mockserver.com/image.jpg'})
    response = in_memory_img_to_img_url(mock_image, mock_upload_url)
    assert 'url' in response
    assert response['url'] == 'https://mockserver.com/image.jpg'
