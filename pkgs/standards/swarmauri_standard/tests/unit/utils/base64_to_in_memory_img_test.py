import pytest
from swarmauri.utils.base64_to_in_memory_img import base64_to_in_memory_img  # Adjust the path
from PIL import Image

@pytest.fixture
def mock_base64():
    import base64
    from io import BytesIO
    img = Image.new('RGB', (150, 150), color='blue')
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

@pytest.mark.unit
def test_base64_to_in_memory_img(mock_base64):
    img = base64_to_in_memory_img(mock_base64)
    assert isinstance(img, Image.Image)
