import pytest
from swarmauri_tool_communitycaptchagenerator.CaptchaGeneratorTool import (
    CaptchaGeneratorTool as Tool,
)


@pytest.mark.unit
def test_name():
    """
    Test if the tool's name is correctly set.
    """
    tool = Tool()
    assert tool.name == "CaptchaGeneratorTool"


@pytest.mark.unit
def test_type():
    """
    Test if the tool's type is correctly set.
    """
    tool = Tool()
    assert tool.type == "CaptchaGeneratorTool"


@pytest.mark.unit
def test_resource():
    """
    Test if the tool's resource is correctly set.
    """
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_serialization():
    """
    Test the serialization functionality of the tool.
    """
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
def test_call():
    tool = Tool()

    # Sample text for CAPTCHA generation
    text = "This is a test CAPTCHA"

    # Call the tool and capture the result
    result = tool(text)

    # Expected keys in the result
    expected_keys = {"image_b64"}

    # Verify that the result is a dictionary
    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"

    # Check if the result contains the 'image_b64' key
    assert expected_keys.issubset(
        result.keys()
    ), f"Expected keys {expected_keys}, but got {result.keys()}"

    # Verify that the 'image_b64' field is a string (base64 encoded image)
    image_b64 = result.get("image_b64")
    assert isinstance(
        image_b64, str
    ), f"Expected string for 'image_b64', but got {type(image_b64).__name__}"
