import pytest
import os
from swarmauri.utils.base64_to_file_path import base64_to_file_path  # Adjust the path

@pytest.fixture
def mock_base64():
    return 'iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAA...'

@pytest.fixture
def mock_file_path(tmp_path):
    return os.path.join(tmp_path, 'test_image.jpg')

@pytest.mark.unit
def test_base64_to_file_path(mock_base64, mock_file_path):
    base64_to_file_path(mock_base64, mock_file_path)
    assert os.path.exists(mock_file_path)
