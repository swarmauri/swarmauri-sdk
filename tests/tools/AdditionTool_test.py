import pytest
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    def test():
        tool = Tool()
        assert tool.resource == 'Tool'
    test()

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'AdditionTool'

@pytest.mark.unit
def test_initialization():
    def test():
        tool = Tool()
        assert type(tool.swm_path) == str
        assert type(tool.id) == str
    test()

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
def test_call():
    def test():
        tool = Tool()
        assert tool(2, 3) == str(5)
        assert tool(10, 10) == str(20)
    test()