import pytest
from swarmauri.messages.concrete import HumanMessage, AgentMessage
from swarmauri.conversations.concrete.MaxSizeConversation import (
    MaxSizeConversation,
)


@pytest.mark.unit
def test_ubc_resource():
    conversation = MaxSizeConversation()
    assert conversation.resource == "Conversation"


@pytest.mark.unit
def test_ubc_type():
    conversation = MaxSizeConversation()
    assert conversation.type == "MaxSizeConversation"


@pytest.mark.unit
def test_serialization():
    conversation = MaxSizeConversation()
    assert (
        conversation.id
        == conversation.model_validate_json(conversation.model_dump_json()).id
    )


@pytest.mark.unit
def test_conversation_max_size():
    conv = MaxSizeConversation(max_size=4)

    # Add messages and check that history doesn't exceed max_size
    conv.add_message(HumanMessage(content="human1"))
    conv.add_message(AgentMessage(content="agent1"))
    conv.add_message(HumanMessage(content="human2"))
    conv.add_message(AgentMessage(content="agent2"))
    conv.add_message(HumanMessage(content="human3"))
    conv.add_message(AgentMessage(content="agent3"))

    assert len(conv.history) == 4
    assert conv.history[0].content == "human2"
    assert conv.history[1].content == "agent2"
    assert conv.history[2].content == "human3"
    assert conv.history[3].content == "agent3"


@pytest.mark.unit
def test_add_message_removes_oldest():
    conv = MaxSizeConversation(max_size=2)

    # Add initial messages
    conv.add_message(HumanMessage(content="human1"))
    conv.add_message(AgentMessage(content="agent1"))

    assert len(conv.history) == 2
    assert conv.history[0].content == "human1"
    assert conv.history[1].content == "agent1"

    # Adding new pair of messages should remove the oldest
    conv.add_message(HumanMessage(content="human2"))
    conv.add_message(AgentMessage(content="agent2"))

    assert len(conv.history) == 2
    assert conv.history[0].content == "human2"
    assert conv.history[1].content == "agent2"


@pytest.mark.unit
def test_history_limit_respected():
    conv = MaxSizeConversation(max_size=3)

    # Adding 5 messages, expecting only the last 3 to be in history
    conv.add_message(HumanMessage(content="human1"))
    conv.add_message(AgentMessage(content="agent1"))
    conv.add_message(HumanMessage(content="human2"))
    conv.add_message(AgentMessage(content="agent2"))
    conv.add_message(HumanMessage(content="human3"))

    assert len(conv.history) == 3
    assert conv.history[0].content == "human2"
    assert conv.history[1].content == "agent2"
    assert conv.history[2].content == "human3"

    # Add another message and ensure history updates correctly
    conv.add_message(AgentMessage(content="agent3"))

    assert len(conv.history) == 2
    assert conv.history[0].content == "human3"
    assert conv.history[1].content == "agent3"


@pytest.mark.unit
def test_enforce_max_size_limit():
    conv = MaxSizeConversation(max_size=4)

    # Adding messages until the limit is reached
    conv.add_message(HumanMessage(content="human1"))
    conv.add_message(AgentMessage(content="agent1"))
    conv.add_message(HumanMessage(content="human2"))
    conv.add_message(AgentMessage(content="agent2"))
    conv.add_message(HumanMessage(content="human3"))
    conv.add_message(AgentMessage(content="agent3"))

    # Ensure only the last 4 messages are kept in history
    assert len(conv.history) == 4
    assert conv.history[0].content == "human2"
    assert conv.history[1].content == "agent2"
    assert conv.history[2].content == "human3"
    assert conv.history[3].content == "agent3"


def test_add_messages():
    conv = MaxSizeConversation(max_size=4)

    # Add multiple messages at once
    messages = [
        HumanMessage(content="human1"),
        AgentMessage(content="agent1"),
        HumanMessage(content="human2"),
        AgentMessage(content="agent2"),
    ]
    conv.add_messages(messages)

    assert len(conv.history) == 4
    assert conv.history[0].content == "human1"
    assert conv.history[1].content == "agent1"
    assert conv.history[2].content == "human2"
    assert conv.history[3].content == "agent2"
