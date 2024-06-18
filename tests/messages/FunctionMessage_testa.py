import pytest
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage

@pytest.mark.unit
def test_ubc_resource():
    def test():
        message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
        assert message.resource == 'Message'
    test()
    
@pytest.mark.unit
def test_name():
    def test():
        message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
        assert message.name == 'test'
    test()

@pytest.mark.unit
def test_content():
    def test():
        message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
        assert message.content == 'test'
    test()

@pytest.mark.unit
def test_role():
    def test():
        message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
        assert message.role == 'tool'
    test()

@pytest.mark.unit
def test_tool_call_id():
    def test():
        message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
        assert message.tool_call_id == 'test_tool_call_id'
    test()