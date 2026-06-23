import pytest
from typing import Any, Dict, Literal, Optional

from swarmauri_agent_skill import SkillAgent
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.skills.SkillBase import SkillBase


@ComponentBase.register_type(AgentBase, "RecordingAgent")
class RecordingAgent(AgentBase):
    llm: Any = None
    calls: list = []
    type: Literal["RecordingAgent"] = "RecordingAgent"

    def exec(self, input_str="", multiturn=True, llm_kwargs: Optional[Dict] = None):
        self.calls.append((input_str, multiturn))
        return input_str

    async def aexec(
        self, input_str="", multiturn=True, llm_kwargs: Optional[Dict] = None
    ):
        self.calls.append((input_str, multiturn))
        return input_str

    def batch(self, inputs, llm_kwargs: Optional[Dict] = None):
        return [self.exec(item, llm_kwargs=llm_kwargs) for item in inputs]

    async def abatch(self, inputs, llm_kwargs: Optional[Dict] = None):
        return [await self.aexec(item, llm_kwargs=llm_kwargs) for item in inputs]


@pytest.fixture
def skill():
    return SkillBase(name="demo", description="Demo skill", instructions="Follow demo.")


def test_skill_agent_applies_skill_context(skill):
    agent = SkillAgent(agent=RecordingAgent(), skills=[skill], turn_mode="single")

    result = agent.exec("hello")

    assert "# Skill: demo" in result
    assert "# User Input\nhello" in result
    assert agent.agent.calls[0][1] is False


@pytest.mark.asyncio
async def test_skill_agent_concurrent_delegates_to_abatch(skill):
    agent = SkillAgent(
        agent=RecordingAgent(),
        skills=[skill],
        turn_mode="multi",
        execution_mode="concurrent",
    )

    result = await agent.aexec(["one", "two"])

    assert len(result) == 2
    assert all("# Skill: demo" in item for item in result)
