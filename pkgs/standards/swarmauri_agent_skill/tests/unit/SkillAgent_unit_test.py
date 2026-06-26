import sys
from typing import Literal

import pytest
from pydantic import ConfigDict

from swarmauri_agent_skill import SkillAgent
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.skills.SkillBase import SkillBase
from swarmauri_standard.conversations.MaxSystemContextConversation import (
    MaxSystemContextConversation,
)
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage


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


@ComponentBase.register_type(SkillBase, "AgentTestSkill")
class AgentTestSkill(SkillBase):
    root_path: str | None = None
    type: Literal["AgentTestSkill"] = "AgentTestSkill"
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)


def resource_value(component):
    resource = component.resource
    return getattr(resource, "value", resource)


@pytest.fixture
def demo_skill():
    return AgentTestSkill(
        name="demo",
        description="Demo skill",
        instructions="Follow demo.",
        metadata={"tags": ["delivery"], "triggers": ["ship"]},
    )


@pytest.fixture
def review_skill():
    return AgentTestSkill(
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
        conversation=MaxSystemContextConversation(system_context="", max_size=20),
        skills=list(skills),
        turn_mode=turn_mode,
        execution_mode=execution_mode,
        require_skill=require_skill,
    )


def test_skill_agent_is_not_nested_agent(demo_skill):
    agent = make_agent(demo_skill)

    assert not hasattr(agent, "agent")
    assert isinstance(agent.conversation, MaxSystemContextConversation)


def test_skill_agent_defaults_to_system_context_conversation(demo_skill):
    agent = SkillAgent(llm=EchoSkillLLM(), skills=[demo_skill])

    assert isinstance(agent.conversation, MaxSystemContextConversation)


def test_skill_agent_component_identity(demo_skill):
    agent = make_agent(demo_skill)
    dumped = agent.model_dump(mode="json")

    assert agent.resource == ResourceTypes.AGENT.value
    assert agent.type == "SkillAgent"
    assert dumped["resource"] == "Agent"
    assert dumped["type"] == "SkillAgent"
    assert dumped["llm"]["resource"] == "LLM"
    assert dumped["llm"]["type"] == "EchoSkillLLM"
    assert dumped["conversation"]["resource"] == "Conversation"
    assert dumped["conversation"]["type"] == "MaxSystemContextConversation"
    assert dumped["skills"][0]["resource"] == "Skill"
    assert dumped["skills"][0]["type"] == "AgentTestSkill"
    assert dumped["skill_execution_tool"]["resource"] == "Tool"
    assert dumped["skill_execution_tool"]["type"] == "SkillExecutionTool"


def test_skill_agent_roundtrip_preserves_component_types_and_behavior(tmp_path):
    skill_dir = tmp_path / "demo"
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "run.py").write_text(
        "print('roundtrip skill command')", encoding="utf-8"
    )
    skill = AgentTestSkill(
        name="demo",
        description="Demo skill",
        instructions="Follow demo.",
        scripts=["scripts/run.py"],
        root_path=str(skill_dir),
    )
    agent = SkillAgent(
        llm=EchoSkillLLM(),
        conversation=MaxSystemContextConversation(system_context="", max_size=20),
        system_context=SystemMessage(content="Base skill-agent policy."),
        skills=[skill],
    )

    restored = SkillAgent.model_validate_json(agent.model_dump_json())

    assert restored.type == "SkillAgent"
    assert resource_value(restored) == "Agent"
    assert restored.llm.type == "EchoSkillLLM"
    assert restored.conversation.type == "MaxSystemContextConversation"
    assert resource_value(restored.conversation) == "Conversation"
    assert restored.system_context.type == "SystemMessage"
    assert restored.system_context.role == "system"
    assert restored.skill_execution_tool.type == "SkillExecutionTool"
    assert resource_value(restored.skill_execution_tool) == "Tool"
    assert restored.skills[0].type == "AgentTestSkill"
    assert resource_value(restored.skills[0]) == "Skill"

    response = restored.exec("hello", skill_names=["demo"])
    command_result = restored.execute_skill_commands(
        "demo", [[sys.executable, "scripts/run.py"]]
    )

    assert response == "systems=1;users=1;last=hello"
    assert "Base skill-agent policy." in restored.conversation.system_context.content
    assert "# Skill: demo" in restored.conversation.system_context.content
    assert command_result["results"][0]["exit_code"] == 0
    assert command_result["results"][0]["stdout"].strip() == "roundtrip skill command"


def test_skill_agent_has_only_skill_execution_tool(demo_skill):
    agent = make_agent(demo_skill)
    toolkit = agent.get_skill_toolkit()

    assert list(toolkit.tools) == ["SkillExecutionTool"]


def test_skill_agent_executes_skill_commands(tmp_path):
    skill_dir = tmp_path / "demo"
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "run.py").write_text(
        "print('agent skill command')", encoding="utf-8"
    )
    skill = AgentTestSkill(
        name="demo",
        description="Demo skill",
        instructions="Follow demo.",
        scripts=["scripts/run.py"],
        root_path=str(skill_dir),
    )
    agent = make_agent(skill)

    result = agent.execute_skill_commands("demo", [[sys.executable, "scripts/run.py"]])

    assert result["results"][0]["exit_code"] == 0
    assert result["results"][0]["stdout"].strip() == "agent skill command"


def test_multiturn_preserves_conversation_history(demo_skill):
    agent = make_agent(demo_skill, turn_mode="multi")

    first = agent.exec("hello")
    second = agent.exec("continue")

    assert first == "systems=1;users=1;last=hello"
    assert second == "systems=1;users=2;last=continue"
    assert len(agent.conversation.history) == 5
    assert len(agent.conversation._history) == 4


def test_single_turn_does_not_mutate_persistent_history(demo_skill):
    agent = make_agent(demo_skill, turn_mode="single")

    result = agent.exec("hello")

    assert result == "systems=1;users=1;last=hello"
    assert agent.conversation.system_context.content == ""
    assert agent.conversation._history == []


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
        "systems=1;users=2;last=two",
    ]


@pytest.mark.asyncio
async def test_async_concurrent_list_inputs(demo_skill):
    agent = make_agent(demo_skill, execution_mode="concurrent", turn_mode="single")

    result = await agent.aexec(["one", "two"])

    assert result == [
        "systems=1;users=1;last=one",
        "systems=1;users=1;last=two",
    ]
    assert agent.conversation.system_context.content == ""
    assert agent.conversation._history == []
