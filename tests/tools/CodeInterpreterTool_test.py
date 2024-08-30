import pytest
from swarmauri.standard.tools.concrete.CodeInterpreterTool import CodeInterpreterTool as Tool

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
def test_call():
    python_code = "print('hello world')"
    tool = Tool()
    assert tool(python_code) == 'hello world\n'