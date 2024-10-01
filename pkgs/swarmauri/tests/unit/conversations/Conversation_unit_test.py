import pytest
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.messages.concrete.HumanMessage import HumanMessage


@pytest.mark.unit
def test_ubc_resource():
    conversation = Conversation()
    assert conversation.resource == "Conversation"


@pytest.mark.unit
def test_ubc_type():
    conversation = Conversation()
    assert conversation.type == "Conversation"


@pytest.mark.unit
def test_serialization():
    conversation = Conversation()
    assert (
        conversation.id
        == Conversation.model_validate_json(conversation.model_dump_json()).id
    )


@pytest.mark.unit
def test_add_message():
    conversation = Conversation()
    message = HumanMessage(content="Test message")
    conversation.add_message(message)
    assert conversation.history[-1] == message


@pytest.mark.unit
def test_add_messages():
    conversation = Conversation()
    messages = [
        HumanMessage(content="Test message 1"),
        HumanMessage(content="Test message 2"),
        HumanMessage(content="Test message 3"),
    ]
    conversation.add_messages(messages)
    assert conversation.history[-len(messages) :] == messages


@pytest.mark.unit
def test_remove_message():
    conversation = Conversation()
    message1 = HumanMessage(content="Test message 1")
    message2 = HumanMessage(content="Test message 2")
    conversation.add_message(message1)
    conversation.add_message(message2)
    conversation.remove_message(message1)
    assert message1 not in conversation.history
