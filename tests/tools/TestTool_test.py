import pytest
from swarmauri.standard.tools.concrete.TestTool import TestTool as tTool

@pytest.mark.unit
def test_initialization():
    def test():
        tool = tTool()
        assert type(tool.path) == str
        assert type(tool.id) == str
    test()

@pytest.mark.unit
def test_call():
    def test():
        tool = tTool()
        success_message = 'Program Opened: calc'
        assert tool('calc') == success_message
    test()
