import pytest
import os
from swarmauri.utils.img_url_to_file_path import img_url_to_file_path  # Adjust the path

@pytest.fixture
def mock_img_url():
    return 'https://via.placeholder.com/150'

@pytest.fixture
def mock_file_path(tmp_path):
    return os.path.join(tmp_path, 'test_image.jpg')

@pytest.mark.unit
def test_img_url_to_file_path(mock_img_url, mock_file_path):
    img_url_to_file_path(mock_img_url, mock_file_path)
    assert os.path.exists(mock_file_path)
