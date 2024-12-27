import pytest
from swarmauri.tools.concrete import TestTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'TestTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.swm_path) == str
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
def test_call():
    tool = Tool()

    expected_keys = {'program'}
    success_message = 'Program Opened: calc'

    result = tool('calc')

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(result.get("program"),
                      str), f"Expected str, but got {type(result.get('program')).__name__}"

    assert result.get(
        "program") == success_message, f"Expected Calculated result {success_message}, but got {result.get('program')}"

