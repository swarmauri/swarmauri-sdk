 import os
import pytest
from swarmauri.standard.tools.concrete.CaptchaGeneratorTool import CaptchaGeneratorTool as Tool

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
    """
    A test case for the call method.
    """
    tool = Tool()
    text = "This is a sample captcha text."
    output_file = "test_captcha.png"
    
    # Call the tool with the text and output file
    tool(text, output_file)
    
    # Check if the file was created
    assert os.path.isfile(output_file)
    
    # Clean up the file after test
    os.remove(output_file)
