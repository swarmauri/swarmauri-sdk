import pytest
from swarmauri.utils.file_path_to_img_url import file_path_to_img_url  # Adjust the path

@pytest.fixture
def mock_file_path(tmp_path):
    return tmp_path / "test_image.jpg"

@pytest.fixture
def mock_upload_url():
    return 'https://mockserver.com/upload'

@pytest.mark.unit
def test_file_path_to_img_url(mock_file_path, mock_upload_url, requests_mock):
    # Create a dummy file
    with open(mock_file_path, 'wb') as f:
        f.write(b'test image data')

    requests_mock.post(mock_upload_url, json={'url': 'https://mockserver.com/image.jpg'})
    response = file_path_to_img_url(mock_file_path, mock_upload_url)
    assert 'url' in response
    assert response['url'] == 'https://mockserver.com/image.jpg'
