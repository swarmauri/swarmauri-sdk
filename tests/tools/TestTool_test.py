import pytest
from swarmauri.standard.tools.concrete.TestTool import TestTool as Tool

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
        success_message = 'Program Opened: calc'
        assert tool('calc') == success_message
    test()
