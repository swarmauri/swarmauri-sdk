import pytest
from swarmauri.messages.concrete import (
    SystemMessage,
    AgentMessage,
    HumanMessage,
    FunctionMessage,
)
from swarmauri.conversations.concrete.SessionCacheConversation import (
    SessionCacheConversation,
)


@pytest.mark.unit
def test_ubc_resource():
    conversation = SessionCacheConversation(
        system_context=SystemMessage(content="systest"), max_size=4
    )
    assert conversation.resource == "Conversation"


@pytest.mark.unit
def test_ubc_type():
    conversation = SessionCacheConversation(
        system_context=SystemMessage(content="systest"), max_size=4
    )
    assert conversation.type == "SessionCacheConversation"


@pytest.mark.unit
def test_serialization():
    conversation = SessionCacheConversation(
        system_context=SystemMessage(content="systest"), max_size=4
    )
    assert (
        conversation.id
        == SessionCacheConversation.model_validate_json(
            conversation.model_dump_json()
        ).id
    )


@pytest.mark.unit
def test_standard_alternating_agent_ending():
    def test(max_size):
        conv = SessionCacheConversation(
            system_context=SystemMessage(content="systest"), max_size=max_size
        )
        conv.add_message(HumanMessage(content="human"))
        conv.add_message(AgentMessage(content="agent"))
        conv.add_message(HumanMessage(content="human2"))
        conv.add_message(AgentMessage(content="agent2"))
        conv.add_message(HumanMessage(content="human3"))
        conv.add_message(AgentMessage(content="agent3"))
        conv.add_message(HumanMessage(content="human4"))
        conv.add_message(AgentMessage(content="agent4"))
        assert conv.history[0].content == "systest"
        if max_size > 1:
            assert conv.history[1].role != "human"
        if not max_size % 2 and max_size == 2:
            assert conv.history[1].content == "human4"
            assert conv.history[2].content == "agent4"
        if not max_size % 2 and max_size == 4:
            assert conv.history[1].content == "human3"
            assert conv.history[2].content == "agent3"
            assert conv.history[3].content == "human4"
            assert conv.history[4].content == "agent4"
        if not max_size % 2 and max_size == 6:
            assert conv.history[1].content == "human2"
            assert conv.history[2].content == "agent2"
            assert conv.history[3].content == "human3"
            assert conv.history[4].content == "agent3"
            assert conv.history[5].content == "human4"
            assert conv.history[6].content == "agent4"

    for max_size in range(2, 7, 1):
        test(max_size)


@pytest.mark.unit
def test_standard_alternating_human_ending():
    def test(max_size):
        conv = SessionCacheConversation(
            system_context=SystemMessage(content="systest"), max_size=max_size
        )
        conv.add_message(HumanMessage(content="human"))
        conv.add_message(AgentMessage(content="agent"))
        conv.add_message(HumanMessage(content="human2"))
        conv.add_message(AgentMessage(content="agent2"))
        conv.add_message(HumanMessage(content="human3"))
        conv.add_message(AgentMessage(content="agent3"))

        assert conv.history[0].content == "systest"
        if max_size > 1:
            assert conv.history[1].role != "human"

        if not max_size % 2 and max_size == 2:
            assert conv.history[1].content == "human3"

        if not max_size % 2 and max_size == 4:
            assert conv.history[1].content == "human2"
            assert conv.history[2].content == "agent2"
            assert conv.history[3].content == "human3"
            assert conv.history[4].content == "agent3"
        if max_size == 5:
            assert conv.history[1].content == "human2"
            assert conv.history[2].content == "agent2"
            assert conv.history[3].content == "human3"
            assert conv.history[4].content == "agent3"
        if not max_size % 2 and max_size == 6:
            assert conv.history[1].content == "human"
            assert conv.history[2].content == "agent"
            assert conv.history[3].content == "human2"
            assert conv.history[4].content == "agent2"
            assert conv.history[5].content == "human3"
            assert conv.history[6].content == "agent3"

    for max_size in range(2, 7, 1):
        test(max_size)


@pytest.mark.unit
def test_agent_message_first():
    def test(max_size):
        conv = SessionCacheConversation(
            system_context=SystemMessage(content="systest"), max_size=max_size
        )
        try:
            conv.add_message(AgentMessage(content="agent"))
        except Exception as e:
            assert str(e) == "The first message in the history must be an HumanMessage."

    for max_size in range(2, 7, 1):
        test(max_size)


@pytest.mark.unit
def test_consecutive_human_messages():
    def test(max_size):
        conv = SessionCacheConversation(
            system_context=SystemMessage(content="systest"), max_size=max_size
        )
        try:
            conv.add_message(HumanMessage(content="human"))
            conv.add_message(AgentMessage(content="agent"))
            conv.add_message(HumanMessage(content="human"))
            conv.add_message(HumanMessage(content="human"))
        except Exception as e:
            assert str(e) == "Cannot have two repeating HumanMessages."

    for max_size in range(2, 7, 1):
        test(max_size)


@pytest.mark.unit
def test_add_messages():
    conversation = SessionCacheConversation(
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
    assert conversation.history[1].content == "human1"
    assert conversation.history[2].content == "agent1"
    assert conversation.history[3].content == "human2"
    assert conversation.history[4].content == "agent2"
