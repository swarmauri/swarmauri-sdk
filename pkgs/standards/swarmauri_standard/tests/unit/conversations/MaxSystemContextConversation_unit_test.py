import pytest
from swarmauri.messages.concrete import (
    SystemMessage,
    AgentMessage,
    HumanMessage,
)
from swarmauri.conversations.concrete.MaxSystemContextConversation import (
    MaxSystemContextConversation,
)


@pytest.mark.unit
def test_ubc_resource():
    conversation = MaxSystemContextConversation()
    assert conversation.resource == "Conversation"


@pytest.mark.unit
def test_ubc_type():
    conversation = MaxSystemContextConversation()
    assert conversation.type == "MaxSystemContextConversation"


@pytest.mark.unit
def test_serialization():
    conversation = MaxSystemContextConversation()
    assert (
        conversation.id
        == conversation.model_validate_json(conversation.model_dump_json()).id
    )


@pytest.mark.unit
def test_enforce_max_size_limit():
    conversation = MaxSystemContextConversation(
        system_context=SystemMessage(content="systest"), max_size=2
    )
    conversation.add_message(HumanMessage(content="human1"))
    conversation.add_message(AgentMessage(content="agent1"))
    conversation.add_message(HumanMessage(content="human2"))
    conversation.add_message(AgentMessage(content="agent2"))
    conversation.add_message(HumanMessage(content="human3"))

    assert len(conversation.history) == 4
    assert conversation.history[0].content == "systest"
    assert conversation.history[1].content == "human2"
    assert conversation.history[2].content == "agent2"


@pytest.mark.unit
def test_invalid_message_type():
    conversation = MaxSystemContextConversation(system_context="systest")

    with pytest.raises(ValueError) as excinfo:
        conversation.add_message("invalid message type")
    assert "Must use a subclass of IMessage" in str(excinfo.value)


@pytest.mark.unit
def test_consecutive_user_messages():
    conversation = MaxSystemContextConversation(
        system_context=SystemMessage(content="systest"), max_size=4
    )
    conversation.add_message(HumanMessage(content="human1"))
    conversation.add_message(AgentMessage(content="agent1"))
    conversation.add_message(HumanMessage(content="human2"))
    conversation.add_message(HumanMessage(content="human3"))

    assert len(conversation.history) == 4
    assert conversation.history[0].content == "systest"
    assert conversation.history[1].content == "human1"
    assert conversation.history[2].content == "agent1"
    assert conversation.history[3].content == "human2"


@pytest.mark.unit
def test_system_context_override():
    conversation = MaxSystemContextConversation(
        system_context=SystemMessage(content="initial context"), max_size=3
    )
    conversation.system_context = SystemMessage(content="new context")

    assert conversation.system_context.content == "new context"
    assert conversation.history[0].content == "new context"


@pytest.mark.unit
def test_add_messages():
    conversation = MaxSystemContextConversation(
        system_context=SystemMessage(content="systest"), max_size=4
    )
    messages = [
        HumanMessage(content="human1"),
        AgentMessage(content="agent1"),
        HumanMessage(content="human2"),
        AgentMessage(content="agent2"),
    ]
    conversation.add_messages(messages)

    assert len(conversation.history) == 5
    assert conversation.history[0].content == "systest"
    assert conversation.history[1].content == "human1"
    assert conversation.history[2].content == "agent1"
    assert conversation.history[3].content == "human2"
    assert conversation.history[4].content == "agent2"
