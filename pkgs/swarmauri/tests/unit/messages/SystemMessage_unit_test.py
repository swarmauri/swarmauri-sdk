import pytest
from swarmauri.messages.concrete.SystemMessage import SystemMessage

@pytest.mark.unit
def test_ubc_resource():
    message = SystemMessage(content='test')
    assert message.resource == 'Message'

@pytest.mark.unit
def test_ubc_type():
    message = SystemMessage(content='test')
    assert message.type == 'SystemMessage'

@pytest.mark.unit
def test_serialization():
    message = SystemMessage(content='test')
    assert message.id == SystemMessage.model_validate_json(message.model_dump_json()).id

@pytest.mark.unit
def test_content():
    message = SystemMessage(content='test')
    assert message.content == 'test'

@pytest.mark.unit
def test_role():
    message = SystemMessage(content='test')
    assert message.role == 'system'