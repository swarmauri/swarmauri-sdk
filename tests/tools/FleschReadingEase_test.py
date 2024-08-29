import pytest
from swarmauri.standard.tools.concrete.FleschReadingEaseTool import FleschReadingEaseTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'FleschReadingEaseTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_call():
    tool = Tool()
    text = "The cat sat on the mat."
    expected_score = 116.145
    assert  tool(text) == pytest.approx(expected_score, rel=1e-2)