import io
import logging

import pytest
from PIL import Image
from swarmauri_ocr_pytesseract.PytesseractOCR import PytesseractOCR
from swarmauri_standard.utils.timeout_wrapper import timeout


# Helper function to create a simple test image with text
def create_test_image(
    text="Hello World", size=(200, 100), color="white", text_color="black"
):
    from PIL import Image, ImageDraw

    image = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), text, fill=text_color)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


@pytest.fixture(scope="module")
def pytesseract_ocr_model():
    try:
        model = PytesseractOCR()
        # Test if tesseract is installed and accessible
        model.extract_text(create_test_image())
        return model
    except Exception as e:
        pytest.skip(f"Skipping tests due to Tesseract installation issues: {str(e)}")


@pytest.fixture
def sample_image_bytes():
    return create_test_image()


@pytest.fixture
def sample_image_path(tmp_path):
    image_path = tmp_path / "test_image.png"
    image_bytes = create_test_image()
    with open(image_path, "wb") as f:
        f.write(image_bytes)
    return str(image_path)


def test_model_type(pytesseract_ocr_model):
    assert pytesseract_ocr_model.type == "PytesseractImg2TextModel"


def test_serialization(pytesseract_ocr_model):
    assert (
        pytesseract_ocr_model.id
        == PytesseractOCR.model_validate_json(
            pytesseract_ocr_model.model_dump_json()
        ).id
    )


def test_supported_languages(pytesseract_ocr_model):
    languages = pytesseract_ocr_model.get_supported_languages()
    assert isinstance(languages, list)
    assert "eng" in languages  # English should be available by default


@timeout(5)
def test_extract_text_from_bytes(pytesseract_ocr_model, sample_image_bytes):
    text = pytesseract_ocr_model.extract_text(image=sample_image_bytes)
    logging.info(f"Extracted text: {text}")
    assert isinstance(text, str)
    assert "Hello" in text


@timeout(5)
def test_extract_text_from_path(pytesseract_ocr_model, sample_image_path):
    text = pytesseract_ocr_model.extract_text(image=sample_image_path)
    assert isinstance(text, str)
    assert "Hello" in text


@timeout(5)
def test_extract_text_from_pil(pytesseract_ocr_model, sample_image_bytes):
    pil_image = Image.open(io.BytesIO(sample_image_bytes))
    text = pytesseract_ocr_model.extract_text(image=pil_image)
    assert isinstance(text, str)
    assert "Hello" in text


@timeout(5)
@pytest.mark.asyncio
async def test_aextract_text(pytesseract_ocr_model, sample_image_bytes):
    text = await pytesseract_ocr_model.aextract_text(image=sample_image_bytes)
    assert isinstance(text, str)
    assert "Hello" in text


@timeout(5)
def test_batch(pytesseract_ocr_model, sample_image_bytes):
    # Create a list of three identical test images
    images = [sample_image_bytes] * 3

    results = pytesseract_ocr_model.batch(images=images)
    assert len(results) == len(images)
    for text in results:
        assert isinstance(text, str)
        assert "Hello" in text


@timeout(5)
@pytest.mark.asyncio
async def test_abatch(pytesseract_ocr_model, sample_image_bytes):
    # Create a list of three identical test images
    images = [sample_image_bytes] * 3

    results = await pytesseract_ocr_model.abatch(images=images)
    assert len(results) == len(images)
    for text in results:
        assert isinstance(text, str)
        assert "Hello" in text


def test_invalid_image_path(pytesseract_ocr_model):
    with pytest.raises(Exception):
        pytesseract_ocr_model.extract_text("nonexistent_image.png")


def test_invalid_image_format(pytesseract_ocr_model):
    with pytest.raises(Exception):
        pytesseract_ocr_model.extract_text(b"invalid image data")


def test_custom_language(pytesseract_ocr_model, sample_image_bytes):
    # Test with explicit English language setting
    text = pytesseract_ocr_model.extract_text(image=sample_image_bytes, language="eng")
    assert isinstance(text, str)
    assert "Hello" in text


def test_custom_config(pytesseract_ocr_model, sample_image_bytes):
    # Test with custom Tesseract configuration
    text = pytesseract_ocr_model.extract_text(
        image=sample_image_bytes,
        config="--psm 6",  # Assume uniform block of text
    )
    assert isinstance(text, str)
    assert "Hello" in text


@pytest.mark.parametrize(
    "test_text",
    [
        "Hello",
        "Testing 123",
        "Special @#$%Characters",
    ],
)
def test_various_text_content(pytesseract_ocr_model, test_text):
    image_bytes = create_test_image(text=test_text)
    extracted_text = pytesseract_ocr_model.extract_text(image=image_bytes)
    assert test_text in extracted_text
