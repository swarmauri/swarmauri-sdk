import pytest
from swarmauri.community.tools.concrete.LexicalDensityTool import LexicalDensityTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'LexicalDensityTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
def test_call():
    tool = Tool()
    input_text = "This is a test sentence."
    expected_lexical_density = tool.calculate_lexical_density(input_text)
    
    assert tool(input_text)['lexical_density'] == pytest.approx(expected_lexical_density, 0.01)

@pytest.mark.unit
def test_call_empty_text():
    tool = Tool()
    input_text = ""
    expected_lexical_density = 0.0
    
    # Call the tool with the empty text and check if it returns 0.0
    assert tool(input_text)['lexical_density'] == expected_lexical_density