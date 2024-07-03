import pytest
from swarmauri.standard.tools.concrete.CodeInterpreterTool import CodeInterpreterTool as Tool

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
        assert type(tool.swm_path) == str
        assert type(tool.id) == str
    test()

@pytest.mark.unit
def test_call():
    def test():
        python_code = "print('hello world')"
        tool = Tool()
        assert tool(python_code) == 'hello world\n'
    test()