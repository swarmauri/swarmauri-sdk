import pytest
from swarmauri.standard.tools.concrete.SMOGIndexTool import SMOGIndexTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'SMOGIndexTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_call():
    tool = Tool()
    input_text = "This is a sample text with some complex sentences and polysyllabic words to test the SMOG Index calculation."
    expected_smog_index = tool.calculate_smog_index(input_text)
    
    # Call the tool with the input text and compare the result to the expected value
    assert tool(input_text) == pytest.approx(expected_smog_index, 0.1)