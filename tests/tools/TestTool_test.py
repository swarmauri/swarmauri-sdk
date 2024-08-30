import pytest
from swarmauri.standard.tools.concrete.TestTool import TestTool as Tool

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
def test_call():
    tool = Tool()
    success_message = 'Program Opened: calc'
    assert tool('calc') == success_message
