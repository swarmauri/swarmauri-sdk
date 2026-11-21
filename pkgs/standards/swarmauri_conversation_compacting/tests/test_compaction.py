import pytest
from swarmauri_base.agents.AgentCompactionMixin import AgentCompactionMixin
from swarmauri_core.agents.IAgentCompaction import IAgentCompaction
from swarmauri_core.conversations.ICompactingConversation import (
    ICompactingConversation,
)
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

from swarmauri_conversation_compacting import CompactingConversation


def make_conversation(**kwargs):
    conversation = CompactingConversation(keep_recent_turns=1, **kwargs)
    conversation.add_messages(
        [
            SystemMessage(content="Keep this instruction."),
            SystemMessage(
                role="developer", content="Keep this instruction too."
            ),
            HumanMessage(content="Explain the requirements " * 20),
            AgentMessage(content="Use Python 3.12."),
            HumanMessage(content="What next?"),
        ]
    )
    return conversation


def test_plan_preview_apply_and_reset():
    conversation = make_conversation()
    assert isinstance(conversation, ICompactingConversation)
    original_messages = list(conversation.messages)
    plan = conversation.plan_compaction()
    assert plan is not None
    assert plan.older_messages == tuple(original_messages[2:4])

    preview = conversation.preview_compaction(plan, "Use Python 3.12.")
    assert conversation.messages == original_messages
    assert conversation.apply_compaction(plan, "Use Python 3.12.")
    assert (
        conversation.messages == original_messages[:2] + original_messages[4:]
    )
    assert [(m.role, m.content) for m in conversation.history] == [
        (m.role, m.content) for m in preview
    ]
    assert conversation.get_last() is original_messages[-1]

    restored = CompactingConversation.model_validate_json(
        conversation.model_dump_json()
    )
    assert isinstance(restored, CompactingConversation)
    assert restored.summary == "Use Python 3.12."
    assert restored.messages == conversation.messages
    restored.clear_history()
    assert restored.history == []
    assert restored.summary is None


def test_previous_summary_and_stale_plan():
    conversation = make_conversation(summary="Previous requirement.")
    plan = conversation.plan_compaction()
    assert plan is not None
    assert plan.previous_summary == "Previous requirement."
    conversation.messages[2].content = "Updated requirements."
    assert not conversation.apply_compaction(plan, "Obsolete summary.")
    assert conversation.summary == "Previous requirement."


@pytest.mark.parametrize("result_id", ["call-1", "unexpected", None])
def test_tool_exchange_must_be_complete(result_id):
    conversation = CompactingConversation(keep_recent_turns=1)
    conversation.add_messages(
        [
            HumanMessage(content="Look it up."),
            AgentMessage(tool_calls=[{"id": "call-1"}]),
        ]
    )
    if result_id is not None:
        conversation.add_message(
            FunctionMessage(
                content="Found it.", name="lookup", tool_call_id=result_id
            )
        )
    conversation.add_messages(
        [AgentMessage(content="Done."), HumanMessage(content="Next query.")]
    )
    active_call = AgentMessage(tool_calls=[{"id": "call-2"}])
    active_result = FunctionMessage(
        content="Current output", name="lookup", tool_call_id="call-2"
    )
    conversation.add_messages([active_call, active_result])

    plan = conversation.plan_compaction()
    if result_id == "call-1":
        assert plan is not None
        assert [m.role for m in plan.older_messages] == [
            "user",
            "assistant",
            "tool",
            "assistant",
        ]
        assert conversation.apply_compaction(plan, "Lookup succeeded.")
        assert conversation.messages[-2:] == [active_call, active_result]
    else:
        assert plan is None


class CompactionAgent(AgentCompactionMixin):
    def _summarize_compaction(self, plan):
        return "Use Python 3.12."

    async def _asummarize_compaction(self, plan):
        return self._summarize_compaction(plan)


def count_tokens(messages):
    return sum(len(message.content.split()) for message in messages)


def test_agent_supports_manual_compaction_and_optional_threshold():
    agent = CompactionAgent(conversation=make_conversation())
    assert isinstance(agent.conversation, CompactingConversation)
    assert isinstance(agent, IAgentCompaction)
    assert not agent.compact_if_needed(count_input_tokens=count_tokens)
    assert not agent.compact(count_input_tokens=lambda messages: 50)
    assert agent.compact(count_input_tokens=count_tokens)

    agent.conversation = Conversation()
    assert not agent.compact(count_input_tokens=count_tokens)


async def run_async_compaction_checks():
    agent = CompactionAgent(
        conversation=make_conversation(trigger_tokens=1000)
    )
    assert not await agent.acompact_if_needed(count_input_tokens=count_tokens)
    agent.conversation.trigger_tokens = count_tokens(
        agent.conversation.history
    )
    assert await agent.acompact_if_needed(count_input_tokens=count_tokens)

    class ReceivingAgent(CompactionAgent):
        async def _asummarize_compaction(self, plan):
            self.conversation.add_message(AgentMessage(content="New reply."))
            return await super()._asummarize_compaction(plan)

    agent = ReceivingAgent(conversation=make_conversation())
    assert not await agent.acompact(count_input_tokens=count_tokens)
    assert agent.conversation.get_last().content == "New reply."
    assert agent.conversation.summary is None


def test_async_threshold_and_concurrent_change():
    # The fake summarizers complete inline and require no event loop.
    with pytest.raises(StopIteration):
        run_async_compaction_checks().send(None)
