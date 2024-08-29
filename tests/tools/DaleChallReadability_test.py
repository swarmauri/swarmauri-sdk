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
    assert tool(10, 10) == str(20)