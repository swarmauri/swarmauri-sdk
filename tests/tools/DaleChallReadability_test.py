import pytest
from swarmauri.standard.tools.concrete.DaleChallReadabilityTool import DaleChallReadabilityTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'DaleChallReadabilityTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_call():
    tool = Tool()
    input_data = {'input_text': 'This is a simple sentence for testing purposes.'}
    expected_output = 6.5
    assert tool(input_data) == pytest.approx(expected_output, rel=1e-2)