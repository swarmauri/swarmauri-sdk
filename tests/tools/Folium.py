import pytest
from swarmauri.standard.tools.concrete.FoliumTool import FoliumTool as Tool

@pytest.mark.unit
def test_name():
    tool = Tool()
    assert tool.name == "FoliumTool"

@pytest.mark.unit
def test_type():
    tool = Tool()
    assert tool.type == "FoliumTool"

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
def test_call():
    tool = Tool()
    input_data = {
        'input_text': "This is a dummy test for the call method."
    }
    
    result = tool(input_data)
    
    assert result is not None
