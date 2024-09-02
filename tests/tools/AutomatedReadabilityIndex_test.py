import pytest
from swarmauri.standard.tools.concrete.AutomatedReadabilityIndexTool import AutomatedReadabilityIndexTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'AutomatedReadabilityIndexTool'

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
    input_data = {'input_text': 'The quick brown fox jumps over the lazy dog.'}
    expected_output = 1.91
    assert tool(input_data) == pytest.approx(expected_output, rel=1e-2)
