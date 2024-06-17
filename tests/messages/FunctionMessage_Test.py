import pytest
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
        assert message.resource == 'Message'
    test()
    
@pytest.mark.unit
def name_test():
    def test():
        message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
        assert message.name == 'test'
    test()

@pytest.mark.unit
def content_test():
    def test():
        message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
        assert message.content == 'test'
    test()

@pytest.mark.unit
def role_test():
    def test():
        message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
        assert message.role == 'tool'
    test()

@pytest.mark.unit
def tool_call_id_test():
    def test():
        message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
        assert message.tool_call_id == 'test_tool_call_id'
    test()