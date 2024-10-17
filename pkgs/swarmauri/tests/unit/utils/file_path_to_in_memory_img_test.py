import pytest
from PIL import Image
from swarmauri.utils.file_path_to_in_memory_img import file_path_to_in_memory_img  # Adjust the path

@pytest.fixture
def mock_file_path(tmp_path):
    img = Image.new('RGB', (150, 150), color='yellow')
    file_path = tmp_path / "test_image.jpg"
    img.save(file_path)
    return file_path

@pytest.mark.unit
def test_file_path_to_in_memory_img(mock_file_path):
    img = file_path_to_in_memory_img(mock_file_path)
    assert isinstance(img, Image.Image)
