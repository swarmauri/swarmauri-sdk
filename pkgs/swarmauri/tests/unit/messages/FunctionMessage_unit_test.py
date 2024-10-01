import pytest
from swarmauri.messages.concrete.FunctionMessage import FunctionMessage

@pytest.mark.unit
def test_ubc_resource():
    message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
    assert message.resource == 'Message'

@pytest.mark.unit
def test_ubc_type():
    message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
    assert message.type == 'FunctionMessage'

@pytest.mark.unit
def test_serialization():
    message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
    assert message.id == FunctionMessage.model_validate_json(message.model_dump_json()).id

@pytest.mark.unit
def test_name():
    message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
    assert message.name == 'test_name'

@pytest.mark.unit
def test_content():
    message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
    assert message.content == 'test'

@pytest.mark.unit
def test_role():
    message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
    assert message.role == 'tool'

@pytest.mark.unit
def test_tool_call_id():
    message = FunctionMessage(name="test_name", content='test', tool_call_id="test_tool_call_id")
    assert message.tool_call_id == 'test_tool_call_id'