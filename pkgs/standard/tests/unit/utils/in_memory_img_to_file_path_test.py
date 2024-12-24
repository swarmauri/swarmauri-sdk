import pytest
import os
from swarmauri.utils.in_memory_img_to_file_path import in_memory_img_to_file_path  # Adjust the path

@pytest.fixture
def mock_image():
    from PIL import Image
    return Image.new('RGB', (150, 150), color='green')

@pytest.fixture
def mock_file_path(tmp_path):
    return os.path.join(tmp_path, 'test_image.jpg')

@pytest.mark.unit
def test_in_memory_img_to_file_path(mock_image, mock_file_path):
    in_memory_img_to_file_path(mock_image, mock_file_path)
    assert os.path.exists(mock_file_path)
