import pytest
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool as Tool
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit

@pytest.mark.unit
def ubc_initialization_test():
    def test():
    	toolkit = Toolkit()
        assert toolkit.resource == 'Toolkit'
    test()

@pytest.mark.unit
def add_tool_test():
    def test():
    	toolkit = Toolkit()
        tool = Tool()
        toolkit.add_tool(tool)
        assert len(toolkit.list_tools()) == 1
    test()
