import base64
import pytest
from swarmauri_tool_qrcodegenerator.QrCodeGeneratorTool import (
    QrCodeGeneratorTool as Tool,
)


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "QrCodeGeneratorTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
@pytest.mark.parametrize(
    "test_data, expected_min_size",
    [
        (
            "Hello, world!",
            100,
        ),  # Example data and expected minimum size of the base64 string
        ("Another test", 100),
        ("", 100),  # Test with empty string
    ],
)
def test_call(test_data: str, expected_min_size: int):
    tool = Tool()

    # Call the tool with test data
    result = tool(test_data)

    # Validate that the result is a dictionary
    assert isinstance(result, dict)

    # Validate that the dictionary contains the 'image_b64' key
    assert "image_b64" in result

    # Validate that 'image_b64' value is a base64-encoded string
    image_b64 = result["image_b64"]
    assert isinstance(image_b64, str)
    assert image_b64  # Ensure it's not an empty string

    # Validate that the base64 string is of reasonable length
    assert len(image_b64) > expected_min_size

    # Optional: Validate that the base64 string can be decoded to image bytes (additional check)
    try:
        decoded_image = base64.b64decode(image_b64)
        assert decoded_image  # Ensure decoded bytes are not empty
    except (base64.binascii.Error, TypeError) as e:
        pytest.fail(f"Base64 decoding failed with error: {e}")
