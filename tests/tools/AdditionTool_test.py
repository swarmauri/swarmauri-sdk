import pytest
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    def test():
        tool = Tool()
        assert tool.resource == 'Tool'
    test()

@pytest.mark.unit
def test_initialization():
    def test():
        tool = Tool()
        assert type(tool.path) == str
        assert type(tool.id) == str
    test()

@pytest.mark.unit
def test_call():
    def test():
        tool = Tool()
        assert tool(2, 3) == str(5)
        assert tool(10, 10) == str(20)
    test()