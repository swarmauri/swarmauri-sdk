import pytest
from swarmauri.tools.concrete import CodeInterpreterTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'CodeInterpreterTool'

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
    python_code = "print('hello world')"

    expected_output = 'hello world\n'
    expected_keys = {'code_output'}

    tool = Tool()

    result = tool(python_code)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(result.get("code_output"), str), f"Expected str, but got {type(result).__name__}"

    assert result.get("code_output") == expected_output, f"Expected Code Output {expected_output}, but got {result.get('code_output')}"
