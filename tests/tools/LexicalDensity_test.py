import pytest
from swarmauri.standard.tools.concrete.LexicalDensityTool import LexicalDensityTool as Tool

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
def test_call():
    tool = Tool()
    assert tool(10, 10) == str(20)