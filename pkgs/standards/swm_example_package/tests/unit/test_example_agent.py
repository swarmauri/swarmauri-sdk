import pytest

from swm_example_package import ExampleAgent


@pytest.fixture
def agent() -> ExampleAgent:
    return ExampleAgent.model_construct()


def test_example_agent_type(agent: ExampleAgent) -> None:
    assert agent.type == "ExampleAgent"


@pytest.mark.asyncio
async def test_example_agent_aexec_returns_exec_result(agent: ExampleAgent) -> None:
    assert await agent.aexec("hello") is None
