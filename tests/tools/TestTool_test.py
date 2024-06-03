from swarmauri.standard.tools.concrete.TestTool import TestTool

def initialize_test():
    test_tool = TestTool()

def assert_call():
    test_tool = TestTool()
    success_message = 'Program Opened: calc'
    assert test_tool('calc') == success_message

initialize_test()
assert_call()

