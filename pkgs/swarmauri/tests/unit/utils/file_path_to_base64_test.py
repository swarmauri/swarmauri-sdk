import pytest
from swarmauri.utils.file_path_to_base64 import file_path_to_base64  # Adjust the path

@pytest.fixture
def mock_file_path(tmp_path):
    file_path = tmp_path / "test_image.jpg"
    with open(file_path, 'wb') as f:
        f.write(b'test image data')
    return file_path

@pytest.mark.unit
def test_file_path_to_base64(mock_file_path):
    img_base64 = file_path_to_base64(mock_file_path)
    assert isinstance(img_base64, str)
    assert img_base64.startswith('iVBOR')  # Checking for common base64 header
