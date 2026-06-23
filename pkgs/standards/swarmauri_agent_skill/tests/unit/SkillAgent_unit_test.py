from typing import Literal

import pytest

from swarmauri_agent_skill import SkillAgent
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.skills.SkillBase import SkillBase
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.AgentMessage import AgentMessage


@ComponentBase.register_type(LLMBase, "EchoSkillLLM")
class EchoSkillLLM(LLMBase):
    type: Literal["EchoSkillLLM"] = "EchoSkillLLM"

    def predict(self, conversation, **kwargs):
        conversation.add_message(AgentMessage(content=self._response(conversation)))
        return conversation

    async def apredict(self, conversation, **kwargs):
        conversation.add_message(AgentMessage(content=self._response(conversation)))
        return conversation

    def stream(self, *args, **kwargs):
        yield ""

    async def astream(self, *args, **kwargs):
        yield ""

    def batch(self, conversations, **kwargs):
        return [self.predict(conversation, **kwargs) for conversation in conversations]

    async def abatch(self, conversations, **kwargs):
        return [
            await self.apredict(conversation, **kwargs)
            for conversation in conversations
        ]

    @staticmethod
    def _response(conversation):
        system_messages = [
            msg.content for msg in conversation.history if msg.role == "system"
        ]
        user_messages = [
            msg.content for msg in conversation.history if msg.role == "user"
        ]
        return f"systems={len(system_messages)};users={len(user_messages)};last={user_messages[-1]}"


@pytest.fixture
def demo_skill():
    return SkillBase(
        name="demo",
        description="Demo skill",
        instructions="Follow demo.",
        metadata={"tags": ["delivery"], "triggers": ["ship"]},
    )


@pytest.fixture
def review_skill():
    return SkillBase(
        name="review",
        description="Review skill",
        instructions="Review carefully.",
        metadata={"tags": ["audit"], "triggers": ["inspect"]},
    )


def make_agent(
    *skills, turn_mode="multi", execution_mode="sequential", require_skill=False
):
    return SkillAgent(
        llm=EchoSkillLLM(),
        conversation=Conversation(),
        skills=list(skills),
        turn_mode=turn_mode,
        execution_mode=execution_mode,
        require_skill=require_skill,
    )


def test_skill_agent_is_not_nested_agent(demo_skill):
    agent = make_agent(demo_skill)

    assert not hasattr(agent, "agent")
    assert isinstance(agent.conversation, Conversation)


def test_multiturn_preserves_conversation_history(demo_skill):
    agent = make_agent(demo_skill, turn_mode="multi")

    first = agent.exec("hello")
    second = agent.exec("continue")

    assert first == "systems=1;users=1;last=hello"
    assert second == "systems=2;users=2;last=continue"
    assert len(agent.conversation.history) == 6


def test_single_turn_does_not_mutate_persistent_history(demo_skill):
    agent = make_agent(demo_skill, turn_mode="single")

    result = agent.exec("hello")

    assert result == "systems=1;users=1;last=hello"
    assert agent.conversation.history == []


def test_explicit_skill_names_selects_only_requested_skill(demo_skill, review_skill):
    agent = make_agent(demo_skill, review_skill)

    result = agent.exec("generic request", skill_names=["review"])

    assert result == "systems=1;users=1;last=generic request"
    system_content = agent.conversation.history[0].content
    assert "# Skill: review" in system_content
    assert "# Skill: demo" not in system_content


def test_select_skills_matches_name_description_tags_and_triggers(
    demo_skill, review_skill
):
    agent = make_agent(demo_skill, review_skill)

    assert [skill.name for skill in agent.select_skills("please use demo")] == ["demo"]
    assert [skill.name for skill in agent.select_skills("needs Review skill")] == [
        "review"
    ]
    assert [skill.name for skill in agent.select_skills("delivery workflow")] == [
        "demo"
    ]
    assert [skill.name for skill in agent.select_skills("inspect this")] == ["review"]


def test_require_skill_raises_when_nothing_matches(demo_skill, review_skill):
    agent = make_agent(demo_skill, review_skill, require_skill=True)

    with pytest.raises(ValueError, match="No matching skill"):
        agent.exec("unrelated")


def test_unknown_explicit_skill_name_raises(demo_skill):
    agent = make_agent(demo_skill)

    with pytest.raises(ValueError, match="Unknown skill"):
        agent.exec("hello", skill_names=["missing"])


def test_sync_list_inputs_process_sequentially(demo_skill):
    agent = make_agent(demo_skill, execution_mode="concurrent")

    result = agent.exec(["one", "two"])

    assert result == [
        "systems=1;users=1;last=one",
        "systems=2;users=2;last=two",
    ]


@pytest.mark.asyncio
async def test_async_concurrent_list_inputs(demo_skill):
    agent = make_agent(demo_skill, execution_mode="concurrent", turn_mode="single")

    result = await agent.aexec(["one", "two"])

    assert result == [
        "systems=1;users=1;last=one",
        "systems=1;users=1;last=two",
    ]
    assert agent.conversation.history == []
