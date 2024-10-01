import pytest
from swarmauri.messages.concrete.HumanMessage import HumanMessage

@pytest.mark.unit
def test_ubc_resource():
    message = HumanMessage(content='test')
    assert message.resource == 'Message'

@pytest.mark.unit
def test_ubc_type():
    message = HumanMessage(content='test')
    assert message.type == 'HumanMessage'

@pytest.mark.unit
def test_serialization():
    message = HumanMessage(content='test')
    assert message.id == HumanMessage.model_validate_json(message.model_dump_json()).id


@pytest.mark.unit
def test_content():
    message = HumanMessage(content='test')
    assert message.content == 'test'

@pytest.mark.unit
def test_role():
    message = HumanMessage(content='test')
    assert message.role == 'user'