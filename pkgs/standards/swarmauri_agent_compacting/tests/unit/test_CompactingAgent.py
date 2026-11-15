import json
from typing import Literal

import pytest
from pydantic import PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_conversation_compacting import CompactingConversation
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

from swarmauri_agent_compacting import CompactingAgent

pytestmark = pytest.mark.unit


@ComponentBase.register_type(LLMBase, "RecordingLLM")
class RecordingLLM(LLMBase):
    type: Literal["RecordingLLM"] = "RecordingLLM"
    summary: str = "Project targets Python 3.12."
    _requests: list = PrivateAttr(default_factory=list)

    def _reply(self, mode, conversation, kwargs):
        history = [
            (message.role, message.content) for message in conversation.history
        ]
        self._requests.append((mode, history, kwargs))
        content = (
            "Next step."
            if isinstance(conversation, CompactingConversation)
            else self.summary
        )
        conversation.add_message(AgentMessage(content=content))
        return conversation

    def predict(self, conversation, **kwargs):
        return self._reply("sync", conversation, kwargs)

    async def apredict(self, conversation, **kwargs):
        return self._reply("async", conversation, kwargs)

    def stream(self, *args, **kwargs):
        raise NotImplementedError

    async def astream(self, *args, **kwargs):
        raise NotImplementedError

    def batch(self, *args, **kwargs):
        raise NotImplementedError

    async def abatch(self, *args, **kwargs):
        raise NotImplementedError


def count_words(messages):
    return sum(len(message.content.split()) for message in messages)


def make_agent(*, trigger_tokens=None, **kwargs):
    conversation = CompactingConversation(
        keep_recent_turns=1,
        trigger_tokens=trigger_tokens,
        summary="Use Apache-2.0.",
        messages=[
            SystemMessage(content="Preserve this instruction."),
            HumanMessage(content="Explain the project requirements. " * 20),
            AgentMessage(content="Use Python 3.12."),
        ],
    )
    return CompactingAgent(
        llm=RecordingLLM(),
        conversation=conversation,
        count_input_tokens=count_words,
        **kwargs,
    )


def check_manual_summary(agent, mode):
    [(request_mode, history, kwargs)] = agent.llm._requests
    assert request_mode == mode
    assert kwargs == {}
    assert [role for role, _ in history] == ["system", "user"]
    transcript = json.loads(history[-1][1])
    assert transcript["previous_summary"] == "Use Apache-2.0."
    assert [message["role"] for message in transcript["older_messages"]] == [
        "user",
        "assistant",
    ]
    assert agent.conversation.summary == agent.llm.summary
    assert agent.conversation.get_last().content == "What next?"


def test_manual_compaction_sync():
    agent = make_agent(trigger_tokens=1000)
    agent.conversation.add_message(HumanMessage(content="What next?"))
    assert agent.compact()
    check_manual_summary(agent, "sync")


@pytest.mark.asyncio
async def test_manual_compaction_async():
    agent = make_agent()
    agent.conversation.add_message(HumanMessage(content="What next?"))
    assert await agent.acompact()
    check_manual_summary(agent, "async")


def check_automatic_summary(agent, mode):
    [(summary_mode, _, summary_kwargs)] = agent.summary_llm._requests
    assert summary_mode == mode
    assert summary_kwargs == {"max_tokens": 64}
    [(main_mode, main_history, main_kwargs)] = agent.llm._requests
    assert main_mode == mode
    assert main_kwargs == {"temperature": 0.2}
    assert main_history == [
        ("system", "Preserve this instruction."),
        (
            "assistant",
            "Summary of earlier conversation:\nProject targets Python 3.12.",
        ),
        ("user", "What next?"),
    ]
    assert agent.conversation.get_last().content == "Next step."


@pytest.fixture
def automatic_agent():
    agent = make_agent(
        summary_llm=RecordingLLM(),
        summary_llm_kwargs={"max_tokens": 64},
        llm_kwargs={"temperature": 0.2},
        max_input_tokens=50,
    )
    agent.conversation.trigger_tokens = (
        count_words(agent.conversation.history) + 2
    )
    return agent


def test_threshold_dispatch_sync(automatic_agent):
    assert automatic_agent.exec("What next?") == "Next step."
    check_automatic_summary(automatic_agent, "sync")


@pytest.mark.asyncio
async def test_threshold_dispatch_async(automatic_agent):
    assert await automatic_agent.aexec("What next?") == "Next step."
    check_automatic_summary(automatic_agent, "async")


@pytest.mark.parametrize("trigger_tokens", [None, 1000])
def test_exec_skips_compaction_if_disabled_or_below_threshold(trigger_tokens):
    agent = make_agent(trigger_tokens=trigger_tokens)
    assert agent.exec("What next?") == "Next step."
    assert len(agent.llm._requests) == 1
    assert agent.conversation.summary == "Use Apache-2.0."


def test_oversize_input_does_not_reach_chat_model(automatic_agent):
    automatic_agent.max_input_tokens = 2
    with pytest.raises(ValueError, match="exceeding max_input_tokens=2"):
        automatic_agent.exec("What next?")
    assert automatic_agent.llm._requests == []
    assert automatic_agent.conversation.get_last().content == "What next?"


@pytest.mark.asyncio
async def test_async_batch_preserves_turn_order():
    agent = make_agent()
    assert await agent.abatch(["First", "Second"]) == [
        "Next step.",
        "Next step.",
    ]
    assert [
        message.content for message in agent.conversation.messages[-4:]
    ] == [
        "First",
        "Next step.",
        "Second",
        "Next step.",
    ]


def test_restore_rebinds_counter_and_keeps_conversation():
    agent = make_agent(summary_llm=RecordingLLM())
    data = agent.model_dump_json()
    assert "count_input_tokens" not in data
    restored = CompactingAgent.model_validate(
        {**json.loads(data), "count_input_tokens": count_words}
    )
    assert isinstance(restored.conversation, CompactingConversation)
    assert isinstance(restored.summary_llm, RecordingLLM)
    assert restored.conversation == agent.conversation
