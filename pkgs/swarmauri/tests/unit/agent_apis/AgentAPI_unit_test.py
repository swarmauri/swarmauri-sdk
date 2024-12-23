import logging
import os
import pytest
from swarmauri.agent_apis.concrete.AgentAPI import AgentAPI
from swarmauri.factories.concrete.AgentFactory import AgentFactory
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.service_registries.concrete.ServiceRegistry import ServiceRegistry
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def groq_model():
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = GroqModel(api_key=API_KEY)
    return llm


@pytest.fixture(scope="module")
def agent_api(groq_model):
    agent = AgentFactory().create("QAAgent", llm=groq_model)
    agent_registry = ServiceRegistry()
    agent_registry.register_service(agent, "agent1")
    return AgentAPI(agent_registry=agent_registry)


@pytest.mark.unit
def test_ubc_resource(agent_api):
    assert agent_api.resource == "AgentAPI"


@pytest.mark.unit
def test_ubc_type(agent_api):
    assert agent_api.type == "AgentAPI"


@pytest.mark.unit
def test_serialization(agent_api):
    assert agent_api.id == AgentAPI.model_validate_json(agent_api.model_dump_json()).id


def test_invoke(agent_api):
    agent_id = "agent1"

    result = agent_api.invoke(agent_id, input_str="Hello")

    logging.info(result)

    assert isinstance(result, str)


def test_invoke_agent_not_found(agent_api):
    agent_id = "nonexistent_agent"

    with pytest.raises(ValueError) as exc_info:
        agent_api.invoke(agent_id)

    assert str(exc_info.value) == f"Agent with ID {agent_id} not found."


@pytest.mark.asyncio
async def test_ainvoke(agent_api):
    agent_id = "agent1"

    result = await agent_api.ainvoke(agent_id, param="value")

    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_ainvoke_agent_not_found(agent_api):
    agent_id = "nonexistent_agent"

    with pytest.raises(ValueError) as exc_info:
        await agent_api.ainvoke(agent_id)

    assert str(exc_info.value) == f"Agent with ID {agent_id} not found."
