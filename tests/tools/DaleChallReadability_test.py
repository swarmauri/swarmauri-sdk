import pytest
from swarmauri.community.tools.concrete.DaleChallReadabilityTool import DaleChallReadabilityTool as Tool

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
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
def test_call():
    tool = Tool()
    input_data = {'input_text': 'This is a simple sentence for testing purposes.'}
    expected_output = 7.98
    assert tool(input_data)['dale_chall_score'] == pytest.approx(expected_output, rel=1e-2)