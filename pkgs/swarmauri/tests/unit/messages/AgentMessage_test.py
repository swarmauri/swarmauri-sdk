import pytest
from swarmauri.messages.concrete.AgentMessage import AgentMessage

@pytest.mark.unit
def test_ubc_resource():
    message = AgentMessage(content='test')
    assert message.resource == 'Message'

@pytest.mark.unit
def test_ubc_type():
    message = AgentMessage(content='test')
    assert message.type == 'AgentMessage'

@pytest.mark.unit
def test_serialization():
    message = AgentMessage(content='test')
    assert message.id == AgentMessage.model_validate_json(message.model_dump_json()).id

@pytest.mark.unit
def test_content():
    message = AgentMessage(content='test')
    assert message.content == 'test'

@pytest.mark.unit
def test_role():
    message = AgentMessage(content='test')
    assert message.role == 'assistant'