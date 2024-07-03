import pytest
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool as Tool
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit

@pytest.mark.unit
def test_ubc_resource():
    toolkit = Toolkit()
    assert toolkit.resource == 'Toolkit'

@pytest.mark.unit
def test_ubc_type():
    toolkit = Toolkit()
    assert toolkit.type == 'Toolkit'

@pytest.mark.unit
def test_serialization():
    toolkit = Toolkit()
    tool_name = 'AdditionTool'
    tool = Tool(name=tool_name)
    toolkit.add_tool(tool)
    assert toolkit.id == Toolkit.model_validate_json(toolkit.model_dump_json()).id
    assert toolkit.get_tool_by_name(tool_name)(1,2) == '3'

@pytest.mark.unit
def test_add_tool():
    toolkit = Toolkit()
    tool = Tool()
    toolkit.add_tool(tool)
    assert len(toolkit.get_tools()) == 1
