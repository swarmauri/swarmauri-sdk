import pytest
import base64
from swarmauri.utils.base64_to_img_url import base64_to_img_url  # Adjust the path

@pytest.fixture
def mock_base64():
    return base64.b64encode(b'test image data').decode('utf-8')

@pytest.fixture
def mock_upload_url():
    return 'https://mockserver.com/upload'

@pytest.mark.unit
def test_base64_to_img_url(mock_base64, mock_upload_url, requests_mock):
    requests_mock.post(mock_upload_url, json={'url': 'https://mockserver.com/image.jpg'})
    response = base64_to_img_url(mock_base64, mock_upload_url)
    assert 'url' in response
    assert response['url'] == 'https://mockserver.com/image.jpg'
